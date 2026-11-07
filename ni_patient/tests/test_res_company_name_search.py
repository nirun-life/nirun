#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestCompanyNameSearch(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # identifier is given so the mixin does not look up a missing ir.sequence
        cls.companies = cls.env["res.company"].create(
            [
                {"name": "Alpha Care Home", "identifier": "HC-0001", "vat": "TH111"},
                {"name": "Bravo Clinic", "identifier": "HC-0002", "vat": "TH222"},
            ]
        )
        cls.alpha, cls.bravo = cls.companies

    def _search(self, name):
        found = self.env["res.company"].name_search(
            name, args=[("id", "in", self.companies.ids)]
        )
        return self.env["res.company"].browse(i for i, _label in found)

    def test_name(self):
        self.assertEqual(self._search("Alpha"), self.alpha)

    def test_identifier(self):
        self.assertEqual(self._search("HC-0002"), self.bravo)

    def test_vat(self):
        self.assertEqual(self._search("TH111"), self.alpha)
