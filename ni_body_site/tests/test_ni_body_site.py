#  Copyright (c) 2026 NSTDA
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


# The parent_store update can detect the cycle (UserError) before the
# constraint does (ValidationError, a UserError subclass): accept both.
class TestBodySiteHierarchy(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        model = cls.env["ni.body.site"]
        cls.root = model.create({"name": "Root", "code": "T-ROOT"})
        cls.child = model.create(
            {"name": "Child", "code": "T-CHILD", "parent_id": cls.root.id}
        )

    def test_parent_allowed(self):
        grandchild = self.env["ni.body.site"].create(
            {"name": "Grandchild", "code": "T-GRAND", "parent_id": self.child.id}
        )
        self.assertEqual(grandchild.parent_id, self.child)
        self.assertTrue(grandchild.parent_path.startswith(self.root.parent_path))

    def test_recursion_rejected(self):
        with self.assertRaises(UserError):
            self.root.parent_id = self.child

    def test_self_parent_rejected(self):
        with self.assertRaises(UserError):
            self.root.parent_id = self.root
