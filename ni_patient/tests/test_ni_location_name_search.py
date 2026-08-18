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

    def _search(self, name):
        # Scoped to this test's own records: unscoped, the pre-fix TRUE leaf returns an arbitrary
        # 100 rows that need not include bravo/charlie, and the assert passes against the bug.
        found = self.env["ni.location"].name_search(
            name, args=[("id", "in", self.locations.ids)]
        )
        return self.env["ni.location"].browse(i for i, _label in found)

    def test_ilike_filters_instead_of_matching_everything(self):
        self.assertEqual(self._search("Alpha"), self.alpha)

    def test_alias_is_still_matched(self):
        self.assertEqual(self._search("WB"), self.bravo)
