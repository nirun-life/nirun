#  Copyright (c) 2026 NSTDA

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestHierarchy(TransactionCase):
    def _check(self, model):
        parent = self.env[model].create({"name": "Parent", "code": "test-parent"})
        child = self.env[model].create(
            {"name": "Child", "code": "test-child", "parent_id": parent.id}
        )
        with self.assertRaises(UserError):
            parent.parent_id = child
            parent.flush_recordset()

    def test_self_parent(self):
        for model in ("ni.goal.state", "ni.goal.achievement"):
            record = self.env[model].create({"name": "Self", "code": f"self-{model}"})
            with self.subTest(model=model), self.assertRaises(UserError):
                record.parent_id = record
                record.flush_recordset()

    def test_state_cycle(self):
        self._check("ni.goal.state")

    def test_achievement_cycle(self):
        self._check("ni.goal.achievement")
