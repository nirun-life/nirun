#  Copyright (c) 2022 Piruin P.

from odoo import _, api, fields, models

from .goal import _goal_state


class GoalAchievement(models.Model):
    _name = "ni.goal.achievement"
    _description = "Goal Achievements Status"
    _inherit = ["coding.base"]
    _order = "sequence"

    display_name = fields.Char(
        "Achievement Status", compute="_compute_display_name", index=True
    )
    parent_id = fields.Many2one("ni.goal.achievement", index=True, ondelete="set null")
    goal_achieved = fields.Boolean(
        default=False,
        help="Indicate whether this achievement means that goal is achieved or not",
    )
    goal_state = fields.Selection(
        _goal_state,
        required=True,
        help="Indicate goal's life-cycle imply by this achievements status",
    )

    def name_get(self):
        return [(rec.id, rec.display_name) for rec in self]

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        for rec in self.filtered(lambda r: r.parent_id):
            rec.update(
                {
                    "goal_achieved": rec.parent_id.goal_achieved,
                    "goal_state": rec.parent_id.goal_state,
                }
            )

    @api.depends("name", "parent_id")
    def _compute_display_name(self):
        for rec in self:
            name = rec.name or ""
            if rec.parent_id:
                name = "{}, {}".format(rec.parent_id.name, rec.name)
            rec.display_name = name

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(_("Error! You cannot create recursive data."))
