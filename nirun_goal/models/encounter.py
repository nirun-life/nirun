#  Copyright (c) 2022 Piruin P.
from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    goal_ids = fields.One2many("ni.goal", "encounter_id")
    goal_count = fields.Integer(compute="_compute_goal_count", store=True)
    goal_achieved_count = fields.Integer(compute="_compute_goal_count", store=True)
    goal_achieved = fields.Float(
        "Achieved (%)", compute="_compute_goal_count", store=True
    )
    goal_need_confirm = fields.Boolean(compute="_compute_goal_count", compute_sudo=True)

    @api.depends("goal_ids", "goal_ids.achievement_id")
    def _compute_goal_count(self):
        for rec in self:
            count = len(rec.goal_ids)
            achieved = len(rec.goal_ids.filtered(lambda g: g.achieved))
            rec.update(
                {
                    "goal_count": count,
                    "goal_achieved_count": achieved,
                    "goal_achieved": (achieved / count) * 100 if count > 0 else 0.0,
                    "goal_need_confirm": len(
                        rec.goal_ids.filtered(lambda g: g.state == "proposed")
                    ),
                }
            )

    def goal_confirm(self):
        self.mapped("goal_ids").filtered_domain(
            [("state", "=", "proposed")]
        ).action_confirm(force=True)

    def open_goal(self):
        self.ensure_one()
        ctx = dict(self.env.context)

        ctx.update(
            {
                "search_default_patient_id": self.id,
                "default_patient_id": self.patient_id.id,
                "default_encounter_id": self.id,
            }
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_goal", "goal_action"
        )
        return dict(action, context=ctx)
