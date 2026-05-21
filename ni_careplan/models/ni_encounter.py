#  Copyright (c) 2025 NSTDA
from odoo import _, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    def action_new_careplan(self):
        self.ensure_one()
        context = dict(self.env.context)
        context.update(
            {
                "default_patient_id": self.patient_id.id,
                "default_encounter_id": self.id,
            }
        )
        return {
            "name": self.env["ni.careplan.wizard"]._description,
            "res_model": "ni.careplan.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
            "view_type": "form",
            "views": [[False, "form"]],
            "context": context,
        }

    def action_careplan(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_encounter_id": self.id,
                "default_patient_id": self.patient_id.id,
                "search_default_group_category_id": True,
            }
        )
        view = {
            "name": _("Careplan"),
            "res_model": "ni.careplan",
            "type": "ir.actions.act_window",
            "target": ctx.pop("target", "current"),
            "view_mode": "kanban,tree,form",
            "domain": [("patient_id", "=", self.patient_id.id)],
            "context": ctx,
        }
        return view
