#  Copyright (c) 2021 NSTDA

from odoo import _, fields, models


class CoverageBenefit(models.Model):
    _name = "ni.coverage.benefit"
    _description = "Coverage Cost to Beneficiary"
    _inherit = "ni.coverage.benefit.base"

    coverage_id = fields.Many2one(
        "ni.coverage", index=True, ondelete="cascade", required=True
    )
    patient_id = fields.Many2one(related="coverage_id.patient_id")

    _sql_constraints = [
        (
            "type_in_coverage__uniq",
            "unique (coverage_id, type_id)",
            _("Beneficiary Type must be unique !"),
        ),
    ]
