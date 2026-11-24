#  Copyright (c) 2026 NSTDA

from lxml import html

from odoo.tests import HttpCase, tagged

from .common import TestPractitionerRoleCommon


@tagged("post_install", "-at_install")
class TestRegister(TestPractitionerRoleCommon, HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.title = cls.env["res.partner.title"].create({"name": "Test Title"})

    def _url(self, company):
        role = self.role.with_company(company)
        self.assertTrue(role.register_location)
        return f"/practitioner/register/{company.id}/{role.access_token}"

    def _form(self, company):
        response = self.url_open(self._url(company))
        self.assertEqual(response.status_code, 200)
        return html.fromstring(response.text).get_element_by_id("practitioner-info")

    def _submit(self, company, **values):
        form = self._form(company)
        data = {**dict(form.fields), **values}
        return self.url_open("/practitioner/register/submit", data=data)

    def _values(self, **values):
        return {
            "login": "L-0001",
            "password": "register-password",  # pragma: allowlist secret
            "title": str(self.title.id),
            "name": "Registered Nurse",
            "mobile": "0800000000",
            "phone": "020000000",
            "email": "registered@example.com",
            **values,
        }

    def test_token_is_per_company(self):
        token = self._url(self.company).rsplit("/", 1)[1]
        self.assertEqual(self.url_open(self._url(self.company)).status_code, 200)
        self.assertEqual(self.url_open(self._url(self.other_company)).status_code, 200)
        for company, value in [
            (self.other_company, token),
            (self.company, "no-such-token"),
        ]:
            response = self.url_open(f"/practitioner/register/{company.id}/{value}")
            self.assertEqual(response.status_code, 404)

    def test_form_lists_the_titles(self):
        options = self._form(self.company).xpath(
            "//select[@name='title']/option/@value"
        )
        self.assertIn(str(self.title.id), options)

    def test_register_creates_an_unverified_user(self):
        response = self._submit(self.company, **self._values())
        self.assertEqual(response.status_code, 200)
        user = self.env["res.users"].search([("login", "=", "L-0001")])
        self.assertEqual(len(user), 1)
        self.assertFalse(user.verified)
        self.assertEqual(user.name, "Registered Nurse")
        self.assertEqual(user.company_ids, self.company)
        self.assertEqual(user.role_line_ids.role_id, self.role)
        if "company_id" in user.role_line_ids._fields:
            self.assertEqual(user.role_line_ids.company_id, self.company)
        self.assertEqual(user.title, self.title)
        self.assertEqual(user.mobile, "0800000000")

    def test_existing_login_is_rejected(self):
        self._submit(self.company, **self._values())
        response = self._submit(self.company, **self._values(name="Someone Else"))
        self.assertIn("License No. already exist", response.text)
        self.assertEqual(
            self.env["res.users"].search([("login", "=", "L-0001")]).name,
            "Registered Nurse",
        )
