#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class ConditionCode(models.Model):
    _name = "ni.condition.code"
    _description = "Condition / Problem"
    _inherit = ["ni.coding"]

    class_id = fields.Many2one("ni.condition.class", required=False)
