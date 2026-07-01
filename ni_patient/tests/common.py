#  Copyright (c) 2021-2023 NSTDA

from unittest.mock import patch

from odoo.tests import common


class TestPatientCommon(common.TransactionCase):
    def setUp(self):
        super(TestPatientCommon, self).setUp()

        patient_admin = self.env["res.users"].create(
            {
                "login": "Patient.User",
                "groups_id": [
                    (4, self.ref("base.group_user"), 0),
                    (4, self.ref("ni_patient.group_admin"), 0),
                ],
                "name": "Patient Admin",
                "email": "p.admin@example.com",
                "password": "admin",
            }
        )
        self.patient_admin = self.env["ni.patient"].with_user(patient_admin)


class TestEncounterAutoCloseCommon(common.TransactionCase):
    """Shared fixtures/helpers for `ni.encounter.class.cron_auto_close()`
    tests, split across baseline behaviour and timezone edge cases."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Auto Close Test Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": cls.partner.id})

        cls.class_midnight = cls.env["ni.encounter.class"].create(
            {
                "name": "Auto Close Midnight Test",
                "auto_close": True,
                "auto_close_midnight": True,
                "auto_close_offset_number": 1,
            }
        )
        cls.class_offset = cls.env["ni.encounter.class"].create(
            {
                "name": "Auto Close Hours Test",
                "auto_close": True,
                "auto_close_midnight": False,
                "auto_close_offset_type": "hours",
                "auto_close_offset_number": 6,
            }
        )
        cls.class_disabled = cls.env["ni.encounter.class"].create(
            {"name": "Auto Close Disabled Test", "auto_close": False}
        )

    def _make_encounter(self, enc_class, state="in-progress", create_date=None):
        encounter = self.env["ni.encounter"].create(
            {"patient_id": self.patient.id, "class_id": enc_class.id}
        )
        encounter.write({"state": state})
        if create_date is not None:
            self.env.cr.execute(
                "UPDATE ni_encounter SET create_date = %s WHERE id = %s",
                (create_date, encounter.id),
            )
            encounter.invalidate_recordset(["create_date"])
        return encounter

    def _run_cron(self, now):
        with patch("odoo.fields.Datetime.now", return_value=now):
            self.env["ni.encounter.class"].cron_auto_close()
