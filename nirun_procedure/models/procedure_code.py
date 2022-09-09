#  Copyright (c) 2022. NSTDA

from odoo import fields, models


class ProcedureCode(models.Model):
    _name = "ni.procedure.code"
    _description = "Procedure Code"
    _inherit = ["coding.base"]

    category_id = fields.Many2one(
        "ni.procedure.category",
        ondelete="set null",
        help="Default category for code but not limit to.",
    )
