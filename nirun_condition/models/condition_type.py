#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models


# TODO remove this after every instance updated to have ni.condition.cls
# Deprecated
class ConditionType(models.Model):
    _name = "ni.condition.type"
    _description = "Condition Type"
    _inherit = ["coding.base"]

    code_ids = fields.One2many(
        "ni.condition.code", "type_id", "Conditions", readonly=True
    )
    code_count = fields.Integer("Conditions Count", compute="_compute_code", store=True)

    @api.depends("code_ids")
    def _compute_code(self):
        for rec in self:
            rec.condition_count = len(rec.code_ids)
