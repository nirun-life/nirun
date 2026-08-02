#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestLocationNameSearch(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.locations = cls.env["ni.location"].create(
            [
                {"name": "Ward Alpha", "alias": "WA"},
                {"name": "Ward Bravo", "alias": "WB"},
                {"name": "Clinic Charlie"},
            ]
        )
        cls.alpha, cls.bravo, cls.charlie = cls.locations

    def _search(self, name, operator="ilike"):
        found = self.env["ni.location"].name_search(name, operator=operator)
        return self.env["ni.location"].browse(i for i, _label in found)

    def test_ilike_filters_instead_of_matching_everything(self):
        self.assertEqual(self._search("Alpha") & self.locations, self.alpha)

    def test_alias_is_still_matched(self):
        self.assertEqual(self._search("WB") & self.locations, self.bravo)

    def test_negated_operator_is_joined_with_and(self):
        # OR here would let `alias not ilike` re-admit what `name not ilike` excluded
        self.assertNotIn(self.alpha, self._search("Alpha", operator="not ilike"))
