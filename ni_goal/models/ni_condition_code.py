#  Copyright (c) 2024 NSTDA

from odoo import fields, models


class Condition(models.Model):
    _inherit = "ni.condition.code"

    goal_code_ids = fields.Many2many(
        "ni.goal.code",
        "ni_condition_code_goal_code_rel",
        "condition_code_id",
        "goal_code_id",
    )
