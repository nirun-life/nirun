#  Copyright (c) 2021-2023. NSTDA

from odoo import fields, models


class ConditionCode(models.Model):
    _name = "ni.condition.code"
    _description = "Condition / Problem"
    _inherit = ["coding.base"]

    type_id = fields.Many2one("ni.condition.type", required=False)
    classification_id = fields.Many2one("ni.condition.cls", required=False)
