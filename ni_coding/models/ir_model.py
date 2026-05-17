#  Copyright (c) 2024 NSTDA
from odoo import api, models


class IrModel(models.Model):
    _inherit = "ir.model"

    def action_open_records(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": self.model,
            "view_mode": "tree,kanban,form",
        }

    @api.model
    def _get_coding_model_names(self):
        base_cls = self.env.registry["ni.coding"]
        return sorted(
            name
            for name, cls in self.env.registry.models.items()
            if name != "ni.coding" and not cls._abstract and issubclass(cls, base_cls)
        )

    @api.model
    def action_open_coding_models(self):
        tree_view_id = self.env.ref("ni_coding.coding_model_view_tree").id
        return {
            "type": "ir.actions.act_window",
            "name": "Coding Models",
            "res_model": "ir.model",
            "view_mode": "tree",
            "views": [(tree_view_id, "tree")],
            "domain": [("model", "in", self._get_coding_model_names())],
            "context": {"create": False, "delete": False},
        }
