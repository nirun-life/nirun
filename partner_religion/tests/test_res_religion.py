#  Copyright (c) 2026 NSTDA

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestReligion(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Religion = cls.env["res.religion"]
        cls.major = cls.Religion.create({"name": "Test Major Faith", "abbr": "TMF"})
        cls.minor = cls.Religion.create(
            {"name": "Test Minor School", "abbr": "TMS", "parent_id": cls.major.id}
        )

    def test_display_name_default(self):
        self.assertEqual(self.minor.display_name, "Test Minor School")

    def test_display_name_context(self):
        minor = self.minor.with_context(show_parent=True)
        self.assertEqual(minor.display_name, "Test Major Faith, Test Minor School")
        minor = self.minor.with_context(show_abbr=True)
        self.assertEqual(minor.display_name, "Test Minor School (TMS)")
        minor = self.minor.with_context(only_abbr=True)
        self.assertEqual(minor.display_name, "TMS")

    def test_name_search_abbr(self):
        ids = [rid for rid, _name in self.Religion.name_search("TMS")]
        self.assertEqual(ids, [self.minor.id])

    def test_name_search_every_word(self):
        ids = [rid for rid, _name in self.Religion.name_search("Minor Test")]
        self.assertEqual(ids, [self.minor.id])
        self.assertFalse(self.Religion.name_search("Minor Major"))

    def test_recursive_parent(self):
        with self.assertRaises(UserError):
            self.major.parent_id = self.minor
