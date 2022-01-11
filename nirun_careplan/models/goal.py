#  Copyright (c) 2022 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_goal_state = [
    ("proposed", "Proposed"),
    ("active", "Active"),
    ("completed", "Completed"),
]


class Goal(models.AbstractModel):
    _name = "ni.goal"
    _description = "Goal"
    _order = "sequence"
    _rec_name = "code_id"

    sequence = fields.Integer(help="Determine the display order", index=True)
    color = fields.Integer(string="Color Index")

    name = fields.Char("Goal", related="code_id.name")
    code_id = fields.Many2one(
        "ni.goal.code",
        "Goal",
        required=True,
        index=True,
        tracking=True,
        ondelete="restrict",
    )
    description = fields.Text()
    priority = fields.Selection(
        [("0", "Undefined"), ("1", "Low"), ("2", "Medium"), ("3", "High")],
        default="0",
        tracking=True,
    )
    achievement_id = fields.Many2one("ni.goal.achievement", tracking=True, copy=False)
    achieved = fields.Boolean(
        related="achievement_id.goal_achieved", store=True, copy=False
    )
    state = fields.Selection(
        _goal_state,
        default="proposed",
        stored=True,
        required=False,
        tracking=True,
        readonly=False,
        group_expand="_group_expand_state",
    )

    @api.onchange("achievement_id")
    def onchange_achievement_id(self):
        for rec in self:
            if rec.achievement_id.goal_state:
                rec.state = rec.achievement_id.goal_state

    @api.model
    def _group_expand_state(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    def copy_data(self, default=None):
        if default is None:
            default = {}
        if "state" not in default:
            default["state"] = "proposed"
        return super(Goal, self).copy_data(default)

    def action_confirm(self, force=False):
        if not force:
            goals = self.filtered(lambda g: g.state != "proposed")
            if goals:
                raise ValidationError(
                    _(
                        "Following goals not in valid state to active!\n"
                        + "\t{} ({})\n".format(g.name, g.state)
                        for g in goals
                    )
                )
        self.write(
            {
                "state": "active",
                "achievement_id": self.env.ref("nirun_careplan.goal_in_progress"),
            }
        )
