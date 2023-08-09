#  Copyright (c) 2021 NSTDA

from odoo import _, fields, models


class InsurancePlanBenefit(models.Model):
    _name = "ni.insurance.plan.benefit"
    _inherit = "ni.coverage.benefit.base"
    _description = "Insurance Plan Cost to Beneficiary"

    plan_id = fields.Many2one(
        "ni.insurance.plan", index=True, required=True, ondelete="cascade"
    )

    _sql_constraints = [
        (
            "type_in_plan__uniq",
            "unique (plan_id, type_id)",
            _("Beneficiary Type must be unique !"),
        ),
    ]
