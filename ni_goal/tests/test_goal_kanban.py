#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestGoalKanban(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Kanban Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.env["ni.goal"].create(
            {
                "name": "Walk",
                "patient_id": cls.patient.id,
                "state_id": cls.env.ref("ni_goal.goal_state_active").id,
            }
        )

    def test_kanban_shows_every_state(self):
        groups = self.env["ni.goal"].read_group(
            [("patient_id", "=", self.patient.id)],
            ["state_id"],
            ["state_id"],
        )
        states = self.env["ni.goal.state"].search([])
        self.assertEqual(len(groups), len(states))
        counts = {g["state_id"][0]: g["state_id_count"] for g in groups}
        self.assertEqual(counts[self.env.ref("ni_goal.goal_state_active").id], 1)
