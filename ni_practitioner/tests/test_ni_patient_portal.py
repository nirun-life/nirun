#  Copyright (c) 2026 NSTDA

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestPractitionerPortal(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_password = "practitioner_portal"  # pragma: allowlist secret
        cls.user = cls.env["res.users"].create(
            {
                "name": "Practitioner Portal Admin",
                "login": "practitioner.portal.admin",
                "password": cls.portal_password,
                "groups_id": [
                    (4, cls.env.ref("base.group_user").id),
                    (4, cls.env.ref("ni_patient.group_admin").id),
                ],
            }
        )
        cls.performer = cls.env["hr.employee"].create(
            {
                "name": "Portal Performer",
                "work_email": "portal.performer@example.com",
                "work_phone": "020000000",
            }
        )
        partner = cls.env["res.partner"].create({"name": "Portal Test Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_AMB").id,
            }
        )

    def _get(self, url):
        self.authenticate(self.user.login, self.portal_password)
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200, url)
        return response.text

    def test_encounters_page(self):
        url = f"/my/patients/{self.patient.id}"
        body = self._get(url)
        self.assertIn("<td>Performer</td>", body)
        self.assertNotIn("Portal Performer", body)
        self.encounter.performer_id = self.performer
        self.assertIn("Portal Performer", self._get(url))

    def test_encounter_page(self):
        url = f"/my/patients/{self.patient.id}/{self.encounter.id}"
        self.assertNotIn("<strong>Performer</strong>", self._get(url))
        self.encounter.performer_id = self.performer
        body = self._get(url)
        self.assertIn("<strong>Performer</strong>", body)
        self.assertIn("Portal Performer", body)
        self.assertIn("portal.performer@example.com", body)
