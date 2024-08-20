#  Copyright (c) 2021-2023 NSTDA

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestPartnerAge(common.TransactionCase):
    def setUp(self):
        super(TestPartnerAge, self).setUp()
        self.partners = self.env["res.partner"]
        self.today = fields.Date.context_today(self.partners)

    def test_age_from_birthdate(self):
        partner = self.partners.create(
            {"name": "partner", "birthdate": self.today - relativedelta(years=34)}
        )

        self.assertEqual(partner.display_age, "34 Years")
        self.assertEqual(partner.age, 34)
        self.assertEqual(partner.deceased, False)

    def test_age_from_age(self):
        partner = self.partners.create({"name": "partner", "age": 34})

        self.assertEqual(partner.age_init, 34)
        self.assertEqual(partner.age_init_date, self.today)
        self.assertEqual(partner.display_age, "34 Years")

    def test_update_from_age_to_birthdate(self):
        partner = self.partners.create({"name": "partner", "age": 34})

        partner.update({"birthdate": self.today - relativedelta(years=36)})

        self.assertEqual(partner.display_age, "36 Years")
        self.assertFalse(partner.age_init)
        self.assertFalse(partner.age_init_date)

    def test_update_from_birthdate_to_age(self):
        partner = self.partners.create(
            {"name": "partner", "birthdate": self.today - relativedelta(years=36)}
        )

        partner.update({"age": 34})

        self.assertFalse(partner.birthdate)

    def test_deceased(self):
        partner = self.partners.create(
            {
                "name": "partner",
                "birthdate": self.today - relativedelta(years=62),
                "deceased_date": self.today - relativedelta(years=2),
            }
        )

        self.assertEqual(partner.display_age, "60 Years")
        self.assertEqual(partner.deceased, True)

    def test_check_deceased(self):
        with self.assertRaises(ValidationError):
            self.partners.create(
                {
                    "name": "partner",
                    "birthdate": self.today - relativedelta(years=34),
                    "deceased_date": self.today - relativedelta(years=47),
                }
            )
        with self.assertRaises(ValidationError):
            self.partners.create(
                {
                    "name": "partner",
                    "deceased_date": self.today + relativedelta(days=47),
                }
            )
