#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Condition(models.Model):
    _inherit = "ni.condition"

    activity_ids = fields.Many2many(
        "ni.careplan.activity",
        "ni_careplan_activity_condition_rel",
        "condition_id",
        "activity_id",
        "Activities",
        readonly=True,
    )
