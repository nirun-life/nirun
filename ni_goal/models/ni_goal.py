#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class Goal(models.Model):
    _name = "ni.goal"
    _description = "Goal"
    _inherit = ["ni.patient.res", "ni.period.mixin"]

    name = fields.Char("Goal Name", required=True, help="Text describing goal")
    code_id = fields.Many2one(
        "ni.goal.code",
        "Goal Code",
        index=True,
        ondelete="restrict",
        help="Code describing goal",
        domain="['|', ('specialty_ids', '=', False), ('specialty_ids', '=', user_specialty)]",
    )
    category_id = fields.Many2one("ni.goal.category")
    category_name = fields.Char("Category Name", related="category_id.name")

    achievement_id = fields.Many2one(
        "ni.goal.achievement",
        index=True,
        ondelete="restrict",
        required=False,
        domain="[('id', 'child_of', state_achievement_ids)]",
    )
    achievement_decoration = fields.Selection(related="achievement_id.decoration")
    achievement_color = fields.Integer(related="achievement_id.color")
    is_achieved = fields.Boolean(default=False, compute="_compute_is_achieved")

    state_id = fields.Many2one(
        "ni.goal.state", index=True, ondelete="restrict", required=True
    )
    state_achievable = fields.Boolean(related="state_id.achievable")
    state_achievement_ids = fields.Many2many(related="state_id.achievement_ids")
    state_decoration = fields.Selection(related="state_id.decoration")

    @api.depends("achievement_id")
    def _compute_is_achieved(self):
        achieved = self.filtered_domain(
            [("achievement_id", "child_of", self.env.ref("ni_goal.goal_achieved").id)]
        )
        if achieved:
            achieved.is_achieved = True
        not_achieved = self - achieved
        if not_achieved:
            not_achieved.is_achieved = False

    @api.onchange("code_id")
    def _onchange_code_id(self):
        for rec in self.filtered(lambda c: c.code_id):
            rec.name = rec.code_id.name
            rec.category_id = rec.code_id.category_id

    @api.onchange("state_id")
    def _onchange_state_id(self):
        for rec in self:
            if rec.achievement_id not in rec.state_achievement_ids:
                rec.achievement_id = rec.state_id.achievement_id or None

    @api.constrains("state_id")
    def _check_state_achievement(self):
        for rec in self:
            if (
                not rec.achievement_id
                or rec.achievement_id not in rec.state_achievement_ids
            ):
                rec.achievement_id = (
                    rec.state_id.achievement_id or rec.state_achievement_ids[0]
                    if rec.state_achievement_ids
                    else None
                )

    def action_mark_achieved(self):
        self.write(
            {
                "state_id": self.env.ref("ni_goal.goal_state_completed"),
                "achievement_id": self.env.ref("ni_goal.goal_achieved"),
            }
        )

    def action_mark_not_achieved(self):
        self.write(
            {
                "state_id": self.env.ref("ni_goal.goal_state_completed"),
                "achievement_id": self.env.ref("ni_goal.goal_not_achieved"),
            }
        )
