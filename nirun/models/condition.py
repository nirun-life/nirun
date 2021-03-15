#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Condition(models.Model):
    _name = "ni.condition"
    _description = "Condition"
    _inherit = ["coding.base"]

    category_id = fields.Many2one("ni.condition.category", required=False)
