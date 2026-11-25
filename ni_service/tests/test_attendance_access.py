#  Copyright (c) 2026 NSTDA

from odoo.exceptions import AccessError
from odoo.tests import new_test_user, tagged

from .common import TestServiceCommon


@tagged("-at_install", "post_install")
class TestAttendanceAccess(TestServiceCommon):
    def setUp(self):
        super().setUp()
        self.line = self.env["ni.encounter.service.attendance"].create(
            {
                "encounter_id": self.encounter.id,
                "attendance_id": self.attendance_slot.id,
                "service_id": self.service.id,
                "service_ids": [(4, self.service.id)],
            }
        )

    def _line_as(self, groups):
        user = new_test_user(self.env, login="attendance.user", groups=groups)
        return self.line.with_user(user)

    def test_viewer_only_reads(self):
        line = self._line_as("ni_patient.group_viewer")
        self.assertEqual(line.read(["encounter_id"])[0]["id"], self.line.id)
        with self.assertRaises(AccessError):
            line.write({"note": "changed"})
        with self.assertRaises(AccessError):
            line.unlink()

    def test_user_writes(self):
        line = self._line_as("ni_patient.group_user")
        line.write({"note": "changed"})
        self.assertEqual(self.line.note, "changed")
        line.unlink()
        self.assertFalse(self.line.exists())

    def test_other_users_have_no_access(self):
        for groups in ("base.group_user", "base.group_portal", "base.group_public"):
            with self.subTest(groups=groups):
                user = new_test_user(self.env, login=f"x.{groups}", groups=groups)
                line = self.line.with_user(user)
                with self.assertRaises(AccessError):
                    line.read(["encounter_id"])
                with self.assertRaises(AccessError):
                    line.write({"note": "changed"})
                with self.assertRaises(AccessError):
                    line.unlink()
