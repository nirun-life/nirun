#  Copyright (c) 2026 NSTDA
"""Every ni.coding model gets the default views from ni_coding (#136, #137).

ni_coding reads its default views from files by view type, so a view type rename
in a new Odoo version (tree -> list in 18.0) would silently stop matching.
"""

from odoo.tests import TransactionCase


class TestCodingDefaultViews(TransactionCase):
    def test_default_views(self):
        coding_models = self.env["ir.model"]._get_coding_model_names()
        self.assertIn("ni.encounter.admit", coding_models)
        list_type = (
            "list"
            if "list" in dict(self.env["ir.ui.view"]._fields["type"].selection)
            else "tree"
        )
        for model_name in coding_models:
            for view_type, root in (
                (list_type, list_type),
                ("kanban", "kanban"),
                ("form", "form"),
            ):
                own_view = self.env["ir.ui.view"].search_count(
                    [("model", "=", model_name), ("type", "=", view_type)]
                )
                if own_view:
                    continue
                arch = self.env[model_name].get_view(view_type=view_type)["arch"]
                self.assertTrue(
                    arch.lstrip().startswith(f"<{root}"),
                    f"{model_name} {view_type}: {arch[:60]}",
                )
                self.assertIn('name="code"', arch, f"{model_name} {view_type}")
