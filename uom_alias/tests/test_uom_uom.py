#  Copyright (c) 2023 NSTDA


from odoo.tests.common import TransactionCase


class TestUoM(TransactionCase):
    def setUp(self):
        super().setUp()
        self.uom = self.env["uom.uom"]
        # gal (US) is archived by default since Odoo 19.
        self.env.ref("uom.product_uom_gal").active = True

    def test_name_search(self):
        gallon = self.uom.name_search("gallon")[0]

        self.assertEqual(gallon[1], "gal (US)")

    def test_alias_data(self):
        self.assertEqual(self.env.ref("uom.product_uom_square_meter").alias, "sq.m.")
        self.assertEqual(self.env.ref("uom.product_uom_square_foot").alias, "sq.ft.")
