#  Copyright (c) 2026 NSTDA

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
        groups = self.env["ni.immunization.evaluation"]._read_group(
            [("patient_id", "=", self.patient.id)],
            ["target_disease_id"],
            ["__count"],
        )
        found = {g["target_disease_id"][0] for g in groups}
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
