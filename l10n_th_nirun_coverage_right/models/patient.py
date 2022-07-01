#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    coverage_plan_id = fields.Many2one(
        "ni.insurance.plan",
        tracking=True,
        ondelete="set null",
        help="Base coverage (Insurance) plan for patient",
    )
    coverage_partner_id = fields.Many2one(
        "res.partner",
        "Coverage Network",
        tracking=True,
        ondelete="set null",
        help="Organization that provide health coverage",
    )
