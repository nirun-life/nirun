#  Copyright (c) 2026 NSTDA

from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("-at_install", "post_install")
class TestCareplanAccess(TransactionCase):
    def setUp(self):
        super().setUp()
        partner = self.env["res.partner"].create({"name": "Careplan Access Patient"})
        patient = self.env["ni.patient"].create({"partner_id": partner.id})
        self.careplan = self.env["ni.careplan"].create({"patient_id": patient.id})

    def _as(self, groups):
        user = new_test_user(self.env, login=f"access.{groups}", groups=groups)
        return self.careplan.with_user(user)

    def test_viewer_only_reads(self):
        record = self._as("ni_patient.group_viewer")
        self.assertEqual(record.read(["patient_id"])[0]["id"], record.id)
        with self.assertRaises(AccessError):
            record.write({"goal_mode": "simple"})
        with self.assertRaises(AccessError):
            record.unlink()

    def test_user_writes(self):
        record = self._as("ni_patient.group_user")
        record.write({"goal_mode": "simple"})
        self.assertEqual(self.careplan.goal_mode, "simple")
        record.unlink()
        self.assertFalse(self.careplan.exists())

    def test_other_users_have_no_access(self):
        for groups in ("base.group_user", "base.group_portal", "base.group_public"):
            with self.subTest(groups=groups):
                record = self._as(groups)
                with self.assertRaises(AccessError):
                    record.read(["patient_id"])
                with self.assertRaises(AccessError):
                    record.write({"goal_mode": "simple"})
                with self.assertRaises(AccessError):
                    record.unlink()
