#  Copyright (c) 2026 NSTDA

from odoo.tests import TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestGoalState(TransactionCase):
    def test_default_achievement_domain(self):
        """The default achievement is chosen among the allowed ones."""
        state = self.env.ref("ni_goal.goal_state_active")
        allowed = state.achievement_ids
        self.assertTrue(allowed)
        domain = safe_eval(
            state._fields["achievement_id"].domain,
            {"achievement_ids": allowed.ids},
        )
        self.assertEqual(self.env["ni.goal.achievement"].search(domain), allowed)
