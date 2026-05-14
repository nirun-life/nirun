#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    careplan_ids = fields.One2many("ni.careplan", "patient_id")
    careplan_count = fields.Integer(compute="_compute_careplan_count")

    goal_ids = fields.One2many("ni.goal", "patient_id")

    @api.depends("careplan_ids")
    def _compute_careplan_count(self):
        for rec in self:
            rec.careplan_count = len(rec.careplan_ids)

    def action_new_careplan(self):
        self.ensure_one()
        context = dict(self.env.context)
        context.update({"default_patient_id": self.id})
        view = {
            "name": self.env["ni.careplan"]._description,
            "res_model": "ni.careplan",
            "type": "ir.actions.act_window",
            "target": context.pop("target", "current"),
            "res_id": context.get("careplan_id", 0),
            "view_type": "form",
            "views": [[False, "form"]],
            "context": context,
        }
        return view

    def action_careplan(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_patient_id": self.id,
                "search_default_group_category_id": True,
            }
        )
        if self.deceased:
            ctx.update({"create": False})
        view = {
            "name": _("Careplan"),
            "res_model": "ni.careplan",
            "type": "ir.actions.act_window",
            "target": ctx.pop("target", "current"),
            "view_mode": "kanban,tree,form",
            "domain": [("patient_id", "=", self.id)],
            "context": ctx,
        }
        return view
