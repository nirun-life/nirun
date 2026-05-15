#  Copyright (c) 2026 NSTDA
from odoo import _, api, fields, models

_TERMINAL_STATES = ["completed", "cancelled", "entered-in-error", "rejected"]


class Encounter(models.Model):
    _inherit = "ni.encounter"

    ongoing_goal_ids = fields.Many2many(
        "ni.goal",
        string="Ongoing Goals",
        compute="_compute_ongoing_goal_ids",
    )
    ongoing_goal_count = fields.Integer(compute="_compute_ongoing_goal_ids")

    @api.depends("patient_id", "patient_id.goal_ids.state_id")
    def _compute_ongoing_goal_ids(self):
        for rec in self:
            if rec.patient_id:
                goals = rec.patient_id.goal_ids.filtered(
                    lambda g: g.state_id.code not in _TERMINAL_STATES
                )
                rec.ongoing_goal_ids = goals
                rec.ongoing_goal_count = len(goals)
            else:
                rec.ongoing_goal_ids = False
                rec.ongoing_goal_count = 0

    def action_goal(self):
        self.ensure_one()
        return {
            "name": _("Goal"),
            "res_model": "ni.goal",
            "type": "ir.actions.act_window",
            "view_mode": "kanban,tree,form",
            "domain": [("patient_id", "=", self.patient_id.id)],
            "context": {
                "default_patient_id": self.patient_id.id,
                "default_encounter_id": self.id,
            },
        }

    def action_new_goal(self):
        self.ensure_one()
        return {
            "name": _("New Goal"),
            "res_model": "ni.goal",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_patient_id": self.patient_id.id,
                "default_encounter_id": self.id,
            },
        }
