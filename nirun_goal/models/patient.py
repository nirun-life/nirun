#  Copyright (c) 2022 Piruin P.
from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    goal_ids = fields.One2many("ni.goal", "patient_id")
    goal_count = fields.Integer(compute="_compute_goal_count", store=True)
    goal_achieved_count = fields.Integer(compute="_compute_goal_count", store=True)

    @api.depends("goal_ids")
    def _compute_goal_count(self):
        for rec in self:
            rec.goal_count = len(rec.goal_ids)
            rec.goal_achieved_count = len(rec.goal_ids.filtered(lambda g: g.achieved))

    def open_goal(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.ids[0],
                "search_default_active": True,
                "default_patient_id": self.ids[0],
            }
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_goal", "goal_action"
        )
        return dict(action, context=ctx)
