#  Copyright (c) 2023 NSTDA

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPartnerAgeRange(TransactionCase):
    def setUp(self):
        super().setUp()
        self.range_model = self.env["res.partner.age.range"]
        self.partner_model = self.env["res.partner"]
        self.range_0_9 = self.env.ref("partner_age.range_0")
        self.partner = self.partner_model.create(
            {
                "name": "Test",
                "birthdate": datetime.today() - relativedelta(years=1, days=10),
            }
        )

    def test_validate_range(self):
        with self.assertRaises(ValidationError):
            self.range_model.create({"name": "Child", "age_from": 1, "age_to": 12})
        with self.assertRaises(ValidationError):
            self.range_model.create({"name": "Teenager", "age_from": 16, "age_to": 15})

    def test_cron_update_age_range_id(self):
        self.partner_model.cron_compute_age()

        self.assertEqual(self.partner.age_range_id, self.range_0_9)
