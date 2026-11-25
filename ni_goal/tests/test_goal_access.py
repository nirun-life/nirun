#  Copyright (c) 2026 NSTDA

from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("-at_install", "post_install")
class TestGoalAccess(TransactionCase):
    def setUp(self):
        super().setUp()
        partner = self.env["res.partner"].create({"name": "Goal Access Patient"})
        patient = self.env["ni.patient"].create({"partner_id": partner.id})
        self.goal = self.env["ni.goal"].create(
            {
                "name": "Goal",
                "patient_id": patient.id,
                "state_id": self.env.ref("ni_goal.goal_state_active").id,
            }
        )

    def _as(self, groups):
        user = new_test_user(self.env, login=f"access.{groups}", groups=groups)
        return self.goal.with_user(user)

    def test_viewer_only_reads(self):
        record = self._as("ni_patient.group_viewer")
        self.assertEqual(record.read(["name"])[0]["id"], record.id)
        with self.assertRaises(AccessError):
            record.write({"name": "Changed"})
        with self.assertRaises(AccessError):
            record.unlink()

    def test_user_writes(self):
        record = self._as("ni_patient.group_user")
        record.write({"name": "Changed"})
        self.assertEqual(self.goal.name, "Changed")
        record.unlink()
        self.assertFalse(self.goal.exists())

    def test_other_users_have_no_access(self):
        for groups in ("base.group_user", "base.group_portal", "base.group_public"):
            with self.subTest(groups=groups):
                record = self._as(groups)
                with self.assertRaises(AccessError):
                    record.read(["name"])
                with self.assertRaises(AccessError):
                    record.write({"name": "Changed"})
                with self.assertRaises(AccessError):
                    record.unlink()

    def test_state_wizard(self):
        wizard = self.env["ni.goal.state.wizard"]
        vals = {"goal_id": self.goal.id, "state_id": self.goal.state_id.id}
        for groups in ("base.group_portal", "ni_patient.group_viewer"):
            with self.subTest(groups=groups), self.assertRaises(AccessError):
                user = new_test_user(self.env, login=f"w.{groups}", groups=groups)
                wizard.with_user(user).create(vals)
        user = new_test_user(self.env, login="w.user", groups="ni_patient.group_user")
        wizard.with_user(user).create(vals).action_confirm()
