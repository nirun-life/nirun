#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class ConditionCategory(models.Model):
    _name = "ni.condition.category"
    _description = "Condition Category"
    _inherit = ["coding.base"]

    condition_ids = fields.One2many("ni.condition", "category_id", readonly=True)
