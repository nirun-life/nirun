#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class ConditionCode(models.Model):
    _inherit = "ni.condition.code"

    category_id = fields.Many2one(
        "ni.condition.category", help="Default category for this condition"
    )

    @api.constrains("category_id")
    def _check_category_color(self):
        for rec in self:
            if rec.category_id and (rec.color != rec.category_id.color):
                rec.color = rec.category_id.color


class Condition(models.Model):
    _inherit = "ni.condition"

    color = fields.Integer(related="code_id.color")
