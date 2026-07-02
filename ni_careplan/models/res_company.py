#  Copyright (c) 2026 NSTDA
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    careplan_category_ids = fields.Many2many(
        "ni.careplan.category",
        "res_company_careplan_category",
        "company_id",
        "category_id",
        string="Shared Careplan Categories",
        domain=[("company_id", "=", False)],
        help="Shared careplan categories this company wants to use, in addition to its own.",
    )
