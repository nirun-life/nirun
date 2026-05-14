#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class GoalAchievement(models.Model):
    _inherit = "ni.goal.achievement"

    careplan = fields.Boolean(
        help="this state will appears on careplan achievement or not"
    )
