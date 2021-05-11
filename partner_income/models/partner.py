#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    def _get_default_income_uom(self):
        return (
            self.env["uom.uom"]
            .search([("measure_type", "=", "working_time")], limit=1, order="id")
            .id
        )

    income_currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )
    income = fields.Monetary(currency_field="income_currency_id")
    income_uom = fields.Many2one(
        "uom.uom",
        "Income per working time unit",
        default=_get_default_income_uom,
        required=False,
        domain=[("measure_type", "=", "working_time")],
        help="Unit of measure for income",
    )
