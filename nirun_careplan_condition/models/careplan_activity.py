#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Activity(models.Model):
    _inherit = "ni.careplan.activity"

    reason_condition_ids = fields.Many2many(
        "ni.condition",
        "ni_careplan_activity_condition_rel",
        "activity_id",
        "condition_id",
        "Conditions",
        help="Why activity is needed",
    )
    reason_condition_id = fields.Many2one(
        "ni.condition", "Condition (Main)", help="Main reason of this activity",
    )
