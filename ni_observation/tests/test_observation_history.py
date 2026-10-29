#  Copyright (c) 2026 NSTDA

from odoo import fields
from odoo.tests import common


class TestObservationHistory(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "History Test Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_IMP").id,
                "period_start": fields.Datetime.now(),
            }
        )
        cls.type_a, cls.type_b = cls.env["ni.observation.type"].create(
            [
                {
                    "name": f"History Test {code}",
                    "code": f"test-history-{code}",
                    "value_type": "int",
                    "min": 0,
                    "max": 100,
                }
                for code in ("a", "b")
            ]
        )

    def _observe(self, obs_type, value, occurrence):
        return self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "type_id": obs_type.id,
                "occurrence": occurrence,
                "value_int": value,
            }
        )

    def test_history_of_several_observations(self):
        """Each observation's history holds its own type only, also when
        several observations are read together."""
        a1 = self._observe(self.type_a, 1, "2025-01-01 08:00:00")
        a2 = self._observe(self.type_a, 2, "2025-01-02 08:00:00")
        b1 = self._observe(self.type_b, 3, "2025-01-02 08:00:00")
        self.env.invalidate_all()
        observations = a2 | b1
        observations.mapped("history_ids")
        self.assertEqual(a2.history_ids, a2 | a1)
        self.assertEqual(a2.history_count, 2)
        self.assertEqual(b1.history_ids, b1)
        self.assertEqual(b1.history_count, 1)
