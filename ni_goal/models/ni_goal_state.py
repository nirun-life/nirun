#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models


class GoalState(models.Model):
    _name = "ni.goal.state"
    _description = "Goal State"
    _inherit = "ni.coding"

    _parent_store = True

    parent_id = fields.Many2one("ni.goal.state", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)

    achievement_id = fields.Many2one(
        "ni.goal.achievement",
        help="Default achievement of this state",
        domain="[('id', 'in' , 'achievement_ids')]",
    )
    achievement_ids = fields.Many2many(
        "ni.goal.achievement", help="Achievements allows in this state"
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


@api.constrains("parent_id")
def _check_parent_id(self):
    if not self._check_recursion():
        raise models.ValidationError(_("Error! You cannot create recursive data."))
