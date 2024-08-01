#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models


class GoalAchievement(models.Model):
    _name = "ni.goal.achievement"
    _description = "Goal Achievement"
    _inherit = "ni.coding"

    _parent_store = True

    parent_id = fields.Many2one("ni.goal.achievement", index=True, ondelete="set null")
    parent_path = fields.Char(index=True, unaccent=False)

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


@api.constrains("parent_id")
def _check_parent_id(self):
    if not self._check_recursion():
        raise models.ValidationError(_("Error! You cannot create recursive data."))
