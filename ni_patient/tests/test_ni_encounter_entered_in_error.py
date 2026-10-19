#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestEncounterEnteredInError(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Error Entry Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.enc_class = cls.env["ni.encounter.class"].search([], limit=1)

    def _make_encounter(self, **vals):
        return self.env["ni.encounter"].create(
            dict(
                {"patient_id": self.patient.id, "class_id": self.enc_class.id},
                **vals,
            )
        )

    def test_entered_in_error_keeps_the_patient_active(self):
        encounter = self._make_encounter()
        encounter.action_entered_in_error()
        self.assertEqual(encounter.state, "entered-in-error")
        self.assertTrue(self.patient.active)
