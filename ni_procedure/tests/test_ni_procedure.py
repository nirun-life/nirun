#  Copyright (c) 2026 NSTDA

from odoo.tests import TransactionCase


class TestProcedure(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["ni.patient"].create(
            {"partner_id": cls.env["res.partner"].create({"name": "Procedure P."}).id}
        )
        cls.employee = cls.env["hr.employee"].create({"name": "Test Performer"})
        cls.code = cls.env["ni.procedure.code"].create(
            {"name": "Test Dressing", "code": "TDR", "duration_hours": 0.5}
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

    def test_name_with_state(self):
        procedure = self._create_procedure(state="completed")
        self.assertEqual(
            procedure.with_context(show_state=True).name_get(),
            [(procedure.id, "Test Dressing (Completed)")],
        )
