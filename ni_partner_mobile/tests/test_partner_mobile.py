#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestPartnerMobile(common.TransactionCase):
    def test_mobile_is_kept_apart_from_phone(self):
        partner = self.env["res.partner"].create(
            {"name": "Mobile Test", "phone": "021234567", "mobile": "0812345678"}
        )
        self.assertEqual(partner.phone, "021234567")
        self.assertEqual(partner.mobile, "0812345678")

    def test_mobile_is_a_number_field(self):
        # SMS and the phone search of phone_validation use every number field.
        self.assertIn("mobile", self.env["res.partner"]._phone_get_number_fields())
        partner = self.env["res.partner"].create(
            {"name": "Mobile Search", "mobile": "0899999999"}
        )
        found = self.env["res.partner"].search(
            [("phone_mobile_search", "=", "0899999999")]
        )
        self.assertIn(partner, found)
