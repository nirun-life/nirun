#  Copyright (c) 2026 NSTDA

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestPatientPortal(HttpCase):
    """The portal pages must not need a module that extends ni_patient."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_password = "patient_portal_admin"  # pragma: allowlist secret
        cls.user = cls.env["res.users"].create(
            {
                "name": "Patient Portal Admin",
                "login": "patient.portal.admin",
                "password": cls.portal_password,
                "groups_id": [
                    (4, cls.env.ref("base.group_user").id),
                    (4, cls.env.ref("ni_patient.group_admin").id),
                ],
            }
        )
        partner = cls.env["res.partner"].create({"name": "Portal Test Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_AMB").id,
                "chief_complaint": "Portal test complaint",
            }
        )

    def _get(self, url):
        self.authenticate(self.user.login, self.portal_password)
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200, url)
        return response.text

    def test_patient_encounters_page(self):
        body = self._get(f"/my/patients/{self.patient.id}")
        self.assertIn(self.encounter.name, body)
        self.assertIn("Portal test complaint", body)

    def test_encounter_page(self):
        body = self._get(f"/my/patients/{self.patient.id}/{self.encounter.id}")
        self.assertIn(self.encounter.name, body)
