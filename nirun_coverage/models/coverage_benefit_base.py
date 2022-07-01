#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class CoverageBenefitBase(models.AbstractModel):
    _name = "ni.coverage.benefit.base"
    _description = "Cost to Beneficiary (Base)"
    _order = "sequence"

    sequence = fields.Integer(index=True, default=0)
    type_id = fields.Many2one("ni.coverage.copay", index=True, required=True)
    value_currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    value = fields.Monetary(currency_field="value_currency_id")
    value_percentage = fields.Float("Value (%)")
