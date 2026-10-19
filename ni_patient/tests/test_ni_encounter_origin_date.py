#  Copyright (c) 2026 NSTDA

from datetime import date, datetime

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestEncounterOriginDate(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tz="Asia/Bangkok"))
        cls.partner = cls.env["res.partner"].create({"name": "Origin Date Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": cls.partner.id})
        cls.hospital = cls.env["res.partner"].create(
            {"name": "Origin Hospital", "is_company": True}
        )
        cls.enc_class = cls.env["ni.encounter.class"].search([], limit=1)

    def _make_encounter(self, **vals):
        return self.env["ni.encounter"].create(
            dict(
                {"patient_id": self.patient.id, "class_id": self.enc_class.id},
                **vals,
            )
        )

    def test_origin_date_requires_origin_partner(self):
        with self.assertRaises(ValidationError):
            self._make_encounter(origin_date=date(2026, 10, 1))

    def test_origin_date_after_period_start(self):
        with self.assertRaises(ValidationError):
            self._make_encounter(
                origin_partner_id=self.hospital.id,
                origin_date=date(2026, 10, 2),
                period_start=datetime(2026, 10, 1, 3, 0),
            )

    def test_origin_date_on_or_before_period_start(self):
        for origin_date in (date(2026, 9, 30), date(2026, 10, 1)):
            encounter = self._make_encounter(
                origin_partner_id=self.hospital.id,
                origin_date=origin_date,
                period_start=datetime(2026, 10, 1, 3, 0),
            )
            self.assertEqual(encounter.origin_date, origin_date)

    def test_origin_date_uses_user_timezone(self):
        # 2026-10-01 20:00 UTC is 2026-10-02 03:00 in Bangkok.
        encounter = self._make_encounter(
            origin_partner_id=self.hospital.id,
            origin_date=date(2026, 10, 2),
            period_start=datetime(2026, 10, 1, 20, 0),
        )
        self.assertEqual(encounter.origin_date, date(2026, 10, 2))

    def test_origin_date_without_period_start(self):
        encounter = self._make_encounter(period_start=datetime(2026, 10, 1, 3, 0))
        encounter.write(
            {
                "period_start": False,
                "origin_partner_id": self.hospital.id,
                "origin_date": date(2026, 10, 2),
            }
        )
        self.assertEqual(encounter.origin_date, date(2026, 10, 2))
