#  Copyright (c) 2026 NSTDA

from odoo import fields
from odoo.exceptions import AccessDenied
from odoo.tools.safe_eval import safe_eval

from .common import TestPractitionerRoleCommon


class TestResUsersRole(TestPractitionerRoleCommon):
    def test_token_and_link_per_company(self):
        other = self.role.with_company(self.other_company)
        self.assertTrue(self.role.access_token)
        self.assertFalse(other.access_token)
        self.assertFalse(other.register_location)
        self.assertFalse(other.register_qr_code)
        other.action_generate_access_token()
        self.assertTrue(other.register_location)
        self.assertNotEqual(self.role.access_token, other.access_token)
        self.assertTrue(
            self.role.register_location.endswith(
                f"/practitioner/register/{self.company.id}/{self.role.access_token}"
            )
        )
        self.assertTrue(self.role.register_qr_code)

    def test_token_is_kept(self):
        token = self.role.access_token
        self.role.action_generate_access_token()
        self.role.action_download_qrcode()
        self.assertEqual(self.role.access_token, token)

    def test_reading_the_link_does_not_write(self):
        other = self.role.with_company(self.other_company)
        other.read(["register_location", "register_qr_code"])
        self.assertFalse(other.access_token)

    def test_user_counts(self):
        for login, verified in [("count.one", True), ("count.two", False)]:
            user = self._create_user(login, verified=verified)
            user.role_line_ids = [fields.Command.create({"role_id": self.role.id})]
        self.role.invalidate_recordset()
        self.assertEqual(self.role.user_count, 2)
        self.assertEqual(self.role.user_to_verify_count, 1)
        domain = self.env.ref("ni_practitioner_role.res_users_in_role_action").domain
        domain = safe_eval(domain, {"active_id": self.role.id})
        for value in (domain, self.role.action_user_in_role()["domain"]):
            self.assertEqual(len(self.env["res.users"].search(value)), 2)

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
        credential = {"login": user.login, "password": password, "type": "password"}
        with self.assertRaises(AccessDenied):
            user.with_user(user)._check_credentials(credential, {"interactive": True})
        user.verified = True
        info = user.with_user(user)._check_credentials(
            credential, {"interactive": True}
        )
        self.assertEqual(info["uid"], user.id)
