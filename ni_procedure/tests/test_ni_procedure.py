#  Copyright (c) 2026 NSTDA

from odoo.tests import Form, TransactionCase


class TestProcedure(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["ni.patient"].create(
            {"partner_id": cls.env["res.partner"].create({"name": "Procedure P."}).id}
        )
        cls.employee = cls.env["hr.employee"].create({"name": "Test Performer"})
        cls.code = cls.env["ni.procedure.code"].create(
            {
                "name": "Test Dressing",
                "code": "TDR",
                "duration_hours": 0.5,
                "category_id": cls.env["ni.procedure.category"]
                .create({"name": "Test Category", "code": "TPC"})
                .id,
            }
        )

    def _create_procedure(self, **kwargs):
        return self.env["ni.procedure"].create(
            {
                "patient_id": self.patient.id,
                "code_id": self.code.id,
                "performer_id": self.employee.id,
                **kwargs,
            }
        )

    def test_summary_with_note(self):
        procedure = self._create_procedure(note="Left arm")
        self.assertEqual(procedure.event_id.summary, "Test Dressing; Left arm")
        procedure.note = False
        self.assertEqual(procedure.event_id.summary, "Test Dressing")

    def test_name(self):
        procedure = self._create_procedure(state="completed")

        def name(**context):
            return procedure.with_context(**context).display_name

        self.assertEqual(name(), "Test Dressing")
        self.assertEqual(name(show_category=True), "Test Category,Test Dressing")
        self.assertEqual(name(show_code=True), "[Test Dressing] TDR")
        self.assertEqual(name(show_patient=True), "Procedure P.: Test Dressing")
        self.assertEqual(name(show_state=True), "Test Dressing (Completed)")
        self.assertIn(procedure.identifier, name(show_identifier=True))

    def test_search_by_name(self):
        procedure = self._create_procedure()
        model = self.env["ni.procedure"]
        self.assertIn(procedure.id, dict(model.name_search("Test Dressing")))
        self.assertIn(procedure.id, dict(model.name_search(procedure.identifier)))
        self.assertNotIn(procedure.id, dict(model.name_search("Nothing")))

    def test_count(self):
        encounter = self.env["ni.encounter"].create(
            {
                "patient_id": self.patient.id,
                "class_id": self.env.ref("ni_patient.class_AMB").id,
            }
        )
        self._create_procedure(encounter_id=encounter.id)
        self._create_procedure()
        self.assertEqual(encounter.procedure_count, 1)
        self.assertEqual(self.patient.procedure_count, 2)
        self.assertEqual(
            encounter.action_procedure()["domain"],
            [("patient_id", "=", self.patient.id)],
        )
        self.assertEqual(
            self.patient.action_procedure()["context"]["default_patient_id"],
            self.patient.id,
        )

    def test_form(self):
        form = Form(self.env["ni.procedure"])
        form.patient_id = self.patient
        form.performer_id = self.employee
        form.code_id = self.code
        self.assertEqual(form.duration_hours, 0.5)
        with self.assertRaises(AssertionError):
            form.outcome_id = self.env["ni.procedure.outcome"].search([], limit=1)
        procedure = form.save()
        procedure.action_complete()
        with Form(procedure) as form:
            form.outcome_id = self.env["ni.procedure.outcome"].search([], limit=1)
        self.assertTrue(procedure.outcome_id)

    def test_states(self):
        procedure = self._create_procedure(state="preparation")
        procedure.action_start()
        self.assertEqual(procedure.state, "in-progress")
        procedure.action_suspend()
        procedure.action_resume()
        procedure.action_complete()
        self.assertEqual(procedure.state, "completed")
        self.assertEqual(procedure.event_id.state, "completed")
