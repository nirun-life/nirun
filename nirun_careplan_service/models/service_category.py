#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class ServiceCategory(models.Model):
    _inherit = "ni.service.category"

    careplan_category_id = fields.Many2one(
        "ni.careplan.category", "Care Plan Category", ondelete="set null"
    )
