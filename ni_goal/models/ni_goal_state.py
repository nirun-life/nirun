#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GoalState(models.Model):
    _name = "ni.goal.state"
    _description = "Goal State"
    _inherit = "ni.coding"

    _parent_store = True

    parent_id = fields.Many2one("ni.goal.state", index=True, ondelete="set null")
    parent_path = fields.Char(index=True)

    achievement_id = fields.Many2one(
        "ni.goal.achievement",
        help="Default achievement of this state",
        domain="[('id', 'in', achievement_ids)]",
    )
    achievement_ids = fields.Many2many(
        "ni.goal.achievement",
        string="Allowed Achievements",
        help="Achievements allows in this state",
    )
    decoration = fields.Selection(
        [
            ("primary", "Primary"),
            ("success", "Success"),
            ("info", "Info"),
            ("warning", "Warning"),
            ("danger", "Danger"),
            ("muted", "Muted"),
        ],
        default="muted",
        required=True,
    )
    achievable = fields.Boolean()
    fold = fields.Boolean(default=False)
    icon = fields.Char(default="fa-circle")

    @api.constrains("parent_id")
    def _check_parent_id(self):
        if self._has_cycle():
            raise ValidationError(
                self.env._("Error! You cannot create recursive data.")
            )
