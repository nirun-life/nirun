#  Copyright (c) 2023 NSTDA


from odoo.tests.common import TransactionCase


class TestUoM(TransactionCase):
    def setUp(self):
        super(TestUoM, self).setUp()
        self.uom = self.env["uom.uom"]

    def test_name_search(self):
        gallon = self.uom.name_search("gallon")[0]

        self.assertEqual(gallon[1], "gal (US)")
