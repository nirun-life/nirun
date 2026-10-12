#  Copyright (c) 2026 NSTDA
"""ni.coding models get the default views from ni_coding (#136, #137).

ni_coding reads its default views from files by view type, so a view type rename
in a new Odoo version (tree -> list in 18.0) would silently stop matching.
"""

from odoo.tests import TransactionCase


class TestCodingDefaultViews(TransactionCase):
    def test_default_views(self):
        list_type = (
            "list"
            if "list" in dict(self.env["ir.ui.view"]._fields["type"].selection)
            else "tree"
        )
        for view_type in (list_type, "kanban", "form"):
            arch = self.env["ni.coding"].get_view(view_type=view_type)["arch"]
            self.assertTrue(
                arch.lstrip().startswith(f"<{view_type}"),
                f"{view_type}: {arch[:60]}",
            )
            self.assertIn('name="code"', arch, view_type)
