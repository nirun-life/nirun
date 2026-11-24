#  Copyright (c) 2026 NSTDA

from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase


class TestImmunization(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["ni.patient"].create(
            {
                "partner_id": cls.env["res.partner"]
                .create({"name": "Immunization P."})
                .id
            }
        )
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_AMB").id,
                "period_start": "2025-12-01 01:00:00",
            }
        )
        cls.employee = cls.env["hr.employee"].create({"name": "Vaccinator"})
        cls.diseases = cls.env["ni.immunization.target.disease"].create(
            [
                {"name": "Test Measles", "code": "TMS", "series_doses": 2},
                {"name": "Test Mumps", "code": "TMP", "series_doses": 1},
            ]
        )
        cls.route = cls.env["ni.immunization.route"].create(
            {
                "name": "Test Route",
                "code": "TRT",
                "site_ids": [
                    (0, 0, {"name": "Test Arm", "code": "TAR"}),
                ],
            }
        )
        cls.vaccine = cls.env["ni.immunization.vaccine"].create(
            {
                "name": "Test MM",
                "code": "TMM",
                "route_id": cls.route.id,
                "target_disease_ids": [(6, 0, cls.diseases.ids)],
            }
        )

    def _create_immunization(self, **kwargs):
        return self.env["ni.immunization"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "vaccine_id": self.vaccine.id,
                "performer_id": self.employee.id,
                "occurrence": "2026-01-01 01:00:00",
                **kwargs,
            }
        )

    def _evaluate(self, immunization):
        action = immunization.action_evaluate()
        wizard = self.env[action["res_model"]].browse(action["res_id"])
        wizard.action_apply()
        return wizard

    def test_evaluate_every_disease(self):
        immunization = self._create_immunization()
        self.assertEqual(immunization.pending_disease_count, 2)
        wizard = self._evaluate(immunization)
        self.assertEqual(wizard.line_ids.target_disease_id, self.diseases)
        self.assertEqual(immunization.pending_disease_count, 0)
        self.assertEqual(immunization.evaluation_count, 2)

    def test_evaluate_without_encounter(self):
        immunization = self._create_immunization(encounter_id=False)
        self._evaluate(immunization)
        self.assertEqual(immunization.evaluation_ids.patient_id, self.patient)
        self.assertEqual(immunization.pending_disease_count, 0)

    def test_onchange_vaccine(self):
        form = Form(self.env["ni.immunization"])
        form.patient_id = self.patient
        form.performer_id = self.employee
        form.vaccine_id = self.vaccine
        immunization = form.save()
        self.assertEqual(immunization.route_id, self.route)
        self.assertEqual(immunization.site_id, self.route.site_ids)

    def test_group_by_disease(self):
        result = (
            self.env["ni.immunization.evaluation"]
            .with_context(read_group_expand=True)
            .web_read_group(
                [("patient_id", "=", self.patient.id)],
                ["target_disease_id"],
                ["__count"],
            )
        )
        found = {group["target_disease_id"][0] for group in result["groups"]}
        self.assertTrue(set(self.diseases.ids) <= found)

    def test_evaluation_form(self):
        form = Form(
            self.env["ni.immunization.evaluation"].with_context(
                default_patient_id=self.patient.id
            )
        )
        form.target_disease_id = self.diseases[0]
        self.assertEqual(form.series_doses, 2)
        evaluation = form.save()
        self.assertEqual(evaluation.protection_status, "partial")
        self.assertEqual(evaluation.event_id.name, "Test Measles")

    def _create_evaluation(self, disease, dose, **kwargs):
        return self.env["ni.immunization.evaluation"].create(
            {
                "patient_id": self.patient.id,
                "target_disease_id": disease.id,
                "dose_number": dose,
                "series_doses": disease.series_doses,
                **kwargs,
            }
        )

    def _summary(self, disease):
        self.env.flush_all()
        self.env.invalidate_all()
        return self.patient.immunization_summary_ids.filtered(
            lambda s: s.target_disease_id == disease
        )

    def test_summary(self):
        measles = self.diseases[0]
        self.assertFalse(self._summary(measles))
        first = self._create_evaluation(measles, 1)
        self.assertEqual(first.protection_status, "partial")
        self.assertEqual(self._summary(measles).protection_status, "partial")
        self.assertEqual(self._summary(measles).dose_progress, "1 / 2")
        second = self._create_evaluation(measles, 2)
        summary = self._summary(measles)
        self.assertEqual(summary.protection_status, "protected")
        self.assertEqual(summary.evaluation_ids, second | first)
        self.assertEqual(self.patient.protected_disease_count, 1)
        self.assertEqual(self.encounter.immunization_summary_ids, summary)
        self._create_evaluation(measles, 3, dose_status="not-valid")
        summary = self._summary(measles)
        self.assertEqual(summary.protection_status, "not-protected")
        action = summary.action_add_evaluation()
        self.assertEqual(action["context"]["default_target_disease_id"], measles.id)

    def test_unique_valid_dose(self):
        self._create_evaluation(self.diseases[0], 1)
        self._create_evaluation(self.diseases[0], 1, dose_status="not-valid")
        with self.assertRaisesRegex(ValidationError, "A valid dose #1 already exists"):
            self._create_evaluation(self.diseases[0], 1)

    def test_evaluation_of_another_disease_or_patient(self):
        immunization = self._create_immunization()
        other = self.env["ni.immunization.target.disease"].create(
            {"name": "Test Rabies", "code": "TRB"}
        )
        with self.assertRaisesRegex(ValidationError, "does not target"):
            self._create_evaluation(other, 1, immunization_id=immunization.id)
        patient = self.env["ni.patient"].create(
            {"partner_id": self.env["res.partner"].create({"name": "Other"}).id}
        )
        with self.assertRaisesRegex(ValidationError, "different patient"):
            self._create_evaluation(
                self.diseases[0],
                1,
                immunization_id=immunization.id,
                patient_id=patient.id,
            )

    def test_evaluation_name(self):
        evaluation = self._create_evaluation(self.diseases[0], 2)
        self.assertEqual(evaluation.display_name, "Test Measles #2")

    def test_name(self):
        immunization = self._create_immunization()

        def name(**context):
            return immunization.with_context(**context).display_name

        self.assertEqual(name(), "Test MM")
        self.assertEqual(name(show_patient=True), "Immunization P.: Test MM")
        self.assertEqual(
            name(show_identifier=True), f"Test MM - {immunization.identifier}"
        )

    def test_search_by_name(self):
        immunization = self._create_immunization()
        model = self.env["ni.immunization"]
        self.assertIn(immunization.id, dict(model.name_search("Test MM")))
        self.assertIn(immunization.id, dict(model.name_search(immunization.identifier)))
        self.assertNotIn(immunization.id, dict(model.name_search("Nothing")))

    def test_count(self):
        self._create_immunization()
        self._create_immunization(encounter_id=False)
        self.assertEqual(self.encounter.immunization_count, 1)
        self.assertEqual(self.patient.immunization_count, 2)
        self.assertTrue(self.encounter.action_immunization())
        self.assertTrue(self.patient.action_immunization())

    def test_workflow_summary(self):
        immunization = self._create_immunization(
            route_id=self.route.id,
            site_id=self.route.site_ids.id,
            lot_number="LOT1",
        )
        self.assertEqual(
            immunization.event_id.summary, "Test Route · Test Arm · LOT1 · Vaccinator"
        )
        self.assertEqual(immunization.event_id.name, "Test MM")

    def test_wizard_of_encounter(self):
        action = self.encounter.action_immunization_evaluation_wizard()
        wizard = (
            self.env[action["res_model"]].with_context(**action["context"]).create({})
        )
        self.assertEqual(wizard.patient_id, self.patient)
        with self.assertRaises(ValidationError):
            wizard.action_next()
        self._create_evaluation(self.diseases[1], 1)
        self.env.flush_all()
        wizard.filter_status = "protected"
        self.assertEqual(wizard.available_disease_ids, self.diseases[1])
        wizard.filter_status = "not-protected"
        self.assertNotIn(self.diseases[1], wizard.available_disease_ids)
        wizard.disease_ids = self.diseases
        wizard.action_next()
        self.assertEqual(wizard.line_ids.target_disease_id, self.diseases)
        wizard.action_back()
        self.assertFalse(wizard.line_ids)
        wizard.disease_ids = self.diseases[0]
        wizard.action_next()
        wizard.line_ids.occurrence = "2026-02-01"
        wizard.action_apply()
        self.assertEqual(self._summary(self.diseases[0]).protection_status, "protected")

    def test_wizard_form(self):
        wizard = self.env["ni.immunization.evaluation.wizard"].create(
            {
                "encounter_id": self.encounter.id,
                "disease_ids": [(6, 0, self.diseases.ids)],
            }
        )
        wizard.action_next()
        with Form(wizard) as form:
            with form.line_ids.edit(0) as line:
                line.dose_number = 1
        self.assertEqual(wizard.line_ids[0].dose_number, 1)
