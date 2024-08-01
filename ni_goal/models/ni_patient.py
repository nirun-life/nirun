#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    goal_ids = fields.One2many("ni.goal", "patient_id")
    goal_count = fields.Integer(compute="_compute_goal_ratio")
    goal_achieved_count = fields.Integer(compute="_compute_goal_ratio")
    goal_ratio = fields.Float(compute="_compute_goal_ratio")

    @api.depends("goal_ids")
    def _compute_goal_ratio(self):
        for rec in self:
            rec.goal_count = len(rec.goal_ids)
            rec.goal_achieved_count = len(
                rec.goal_ids.filtered_domain(
                    [
                        (
                            "achievement_id",
                            "child_of",
                            self.env.ref("ni_goal.goal_achieved").id,
                        )
                    ]
                )
            )
            rec.goal_ratio = rec.goal_achieved_count / rec.goal_count * 100
