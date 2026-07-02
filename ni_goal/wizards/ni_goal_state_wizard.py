#  Copyright (c) 2025 NSTDA
from odoo import api, fields, models


class GoalStateWizard(models.TransientModel):
    _name = "ni.goal.state.wizard"
    _description = "Goal State Wizard"

    goal_id = fields.Many2one(
        "ni.goal", string="Goal", required=True, ondelete="cascade"
    )
    state_id = fields.Many2one(
        "ni.goal.state", string="State", required=True, ondelete="restrict"
    )
    state_achievement_ids = fields.Many2many(related="state_id.achievement_ids")
    achievement_id = fields.Many2one(
        "ni.goal.achievement",
        ondelete="restrict",
        domain="[('id', 'in', state_achievement_ids)]",
    )

    # Observation display fields
    observation_type_id = fields.Many2one(related="goal_id.observation_type_id")
    target_value_type = fields.Selection(related="goal_id.target_value_type")
    target_min = fields.Float(related="goal_id.target_min")
    target_max = fields.Float(related="goal_id.target_max")
    target_unit_id = fields.Many2one(related="goal_id.observation_type_id.unit_id")
    target_code_operator = fields.Selection(related="goal_id.target_code_operator")
    target_code_ids = fields.Many2many(related="goal_id.target_code_ids")
    address_observation_id = fields.Many2one(related="goal_id.address_observation_id")
    address_occurrence = fields.Datetime(
        related="goal_id.address_observation_id.occurrence"
    )
    observation_id = fields.Many2one(
        "ni.observation", compute="_compute_latest", string="Latest"
    )
    observation_occurrence = fields.Datetime(compute="_compute_latest")

    note = fields.Html()

    @api.depends("goal_id")
    def _compute_latest(self):
        for wiz in self:
            obs = wiz.goal_id.observation_id
            wiz.observation_id = obs
            wiz.observation_occurrence = obs.occurrence if obs else False

    def action_confirm(self):
        vals = {"state_id": self.state_id.id}
        if self.achievement_id:
            vals["achievement_id"] = self.achievement_id.id
        self.goal_id.write(vals)
        if self.note:
            self.goal_id.message_post(body=self.note, subtype_xmlid="mail.mt_comment")
