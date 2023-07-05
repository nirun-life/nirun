#  Copyright (c) 2022. NSTDA

from odoo import fields, models


class ProcedureCode(models.Model):
    _name = "ni.procedure.code"
    _description = "Procedure Code"
    _inherit = ["ni.coding"]

    category_id = fields.Many2one(
        "ni.procedure.category",
        ondelete="set null",
        help="Default category for code but not limit to.",
    )
    duration_hours = fields.Float("Duration")
