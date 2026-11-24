#  Copyright (c) 2026 NSTDA

from odoo import fields
from odoo.exceptions import AccessDenied

from .common import TestPractitionerRoleCommon


class TestResUsersRole(TestPractitionerRoleCommon):
    def test_token_and_link_per_company(self):
        other = self.role.with_company(self.other_company)
        self.assertTrue(self.role.register_location)
        self.assertTrue(other.register_location)
        self.assertTrue(self.role.access_token)
        self.assertNotEqual(self.role.access_token, other.access_token)
        self.assertTrue(
            self.role.register_location.endswith(
                f"/practitioner/register/{self.company.id}/{self.role.access_token}"
            )
        )
        self.assertTrue(self.role.register_qr_code)

    def test_user_counts(self):
        for login, verified in [("count.one", True), ("count.two", False)]:
            user = self._create_user(login, verified=verified)
            user.role_line_ids = [fields.Command.create({"role_id": self.role.id})]
        self.role.invalidate_recordset()
        self.assertEqual(self.role.user_count, 2)
        self.assertEqual(self.role.user_to_verify_count, 1)

    def test_verify_creates_the_employee(self):
        user = self._create_user("12345", verified=False)
        user.role_line_ids = [fields.Command.create({"role_id": self.role.id})]
        user.action_verify()
        self.assertTrue(user.verified)
        self.assertEqual(user.employee_id.license_no, "12345")
        self.assertEqual(user.employee_id.category_ids, self.category)

    def test_unverified_user_cannot_log_in(self):
        password = "not-verified-yet"  # pragma: allowlist secret
        user = self._create_user("unverified", password=password, verified=False)
        with self.assertRaises(AccessDenied):
            user.with_user(user)._check_credentials(password, {"interactive": True})
        user.verified = True
        user.with_user(user)._check_credentials(password, {"interactive": True})
