#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    coverage_plan_id = fields.Many2one(
        "ni.insurance.plan",
        ondelete="set null",
        help="Base coverage (Insurance) plan for patient",
    )
