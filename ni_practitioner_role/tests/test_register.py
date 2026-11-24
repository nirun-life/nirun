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

    def test_link_with_a_trailing_slash(self):
        response = self.url_open(self._url(self.company) + "/")
        self.assertEqual(response.status_code, 200)
        response = self.url_open(
            f"/practitioner/register/{self.company.id}/no-such-token/"
        )
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

    def _csrf(self):
        form = html.fromstring(self.url_open("/web/login").text)
        return form.xpath("//input[@name='csrf_token']/@value")[0]

    def _post(self, **values):
        """Post what the form would not send"""
        data = {
            "csrf_token": self._csrf(),
            "company_id": str(self.company.id),
            "token": self._url(self.company).rsplit("/", 1)[1],
            **self._values(),
            **values,
        }
        return self.url_open("/practitioner/register/submit", data=data)

    def _registered(self, login="L-0001"):
        return self.env["res.users"].search([("login", "=", login)])

    def test_submit_needs_a_valid_token(self):
        other_token = self._url(self.other_company).rsplit("/", 1)[1]
        role = self.env["res.users.role"].create({"name": "Role of the company"})
        for token in ("no-such-token", "", other_token):
            with self.subTest(token=token):
                response = self._post(token=token, role_id=str(role.id))
                self.assertEqual(response.status_code, 404)
        for company in ("", "x", "0", "999999999"):
            with self.subTest(company=company):
                self.assertEqual(self._post(company_id=company).status_code, 404)
        self.assertFalse(self._registered())

    def test_submit_takes_the_role_of_the_token(self):
        other = self.env["res.users.role"].create({"name": "Other role"})
        self._post(role_id=str(other.id))
        self.assertEqual(self._registered().role_line_ids.role_id, self.role)

    def test_submit_cannot_change_another_account(self):
        victim = self._create_user("victim")
        response = self._post(login="victim", registered="True")
        self.assertIn("License No. already exist", response.text)
        self.assertFalse(victim.role_line_ids)

    def test_submit_is_post_only(self):
        token = self._url(self.company).rsplit("/", 1)[1]
        self.url_open(
            "/practitioner/register/submit"
            f"?company_id={self.company.id}&token={token}&login=L-0001"
            f"&password=register-password&name=Nurse&role_id={self.role.id}"
        )
        self.assertFalse(self._registered())

    def test_form_ignores_the_query_string(self):
        url = self._url(self.company) + "?error=Injected&err=Injected&post=Injected"
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Injected", response.text)

    def _signed_in(self, login, **vals):
        password = "signed-in-password"  # pragma: allowlist secret
        user = self._create_user(login, password=password, **vals)
        self.authenticate(login, password)
        return user

    def test_signed_in_user_gets_the_role(self):
        user = self._signed_in("signed.in")
        victim = self._create_user("victim")
        for _attempt in range(2):  # the second one must not fail
            response = self._submit(self.company, login="victim")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Congratulations", response.text)
        self.assertEqual(user.role_line_ids.role_id, self.role)
        self.assertEqual(len(user.role_line_ids), 1)
        self.assertFalse(victim.role_line_ids)

    def test_signed_in_user_of_another_company(self):
        user = self._signed_in("signed.in")
        self.assertNotIn(self.other_company, user.company_ids)
        response = self._submit(self.other_company)
        self.assertIn("You do not have access to this company", response.text)
        self.assertFalse(user.role_line_ids)
