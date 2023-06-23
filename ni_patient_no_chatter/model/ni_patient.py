#  Copyright (c) 2023 NSTDA
from odoo import models


class Patient(models.Model):
    _inherit = "ni.patient"

    def action_no_chatter_toggle(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx["no_chatter"] = not self.env.context.get("no_chatter", True)
        view = {
            "name": self.name,
            "res_model": "ni.patient",
            "type": "ir.actions.act_window",
            "target": self.env.context.get("target", "main"),
            "res_id": self.ids[0],
            "view_type": "form",
            "views": [[False, "form"]],
            "context": ctx,
        }
        return view
