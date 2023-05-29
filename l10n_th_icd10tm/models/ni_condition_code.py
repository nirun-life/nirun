#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class ConditionCode(models.Model):
    _inherit = "ni.condition.code"

    chapter_id = fields.Many2one(
        "ni.condition.chapter", related="block_id.chapter_id", store=True
    )
    block_id = fields.Many2one("ni.condition.block")
    level = fields.Integer(default=1)
    type = fields.Selection(
        [("code", "Code"), ("header", "Header")], default="code", required=True
    )
