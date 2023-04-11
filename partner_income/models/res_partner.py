#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    def _get_default_income_uom(self):
        return (
            self.env["uom.uom"]
            .search(
                domain=[
                    ("category_id", "=", self.env.ref("uom.uom_categ_wtime").id),
                    ("uom_type", "=", "reference"),
                ],
                limit=1,
                order="id",
            )
            .id
        )

    income_currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )
    income = fields.Monetary(currency_field="income_currency_id", tracking=True)
    income_uom = fields.Many2one(
        "uom.uom",
        "Income per working time unit",
        default=lambda self: self._get_default_income_uom(),
        domain="[('category_id', '=', income_uom_categ)]",
        required=False,
        tracking=True,
        help="Unit of measure for income",
    )
    income_uom_categ = fields.Many2one(
        "uom.category",
        default=lambda self: self.env.ref("uom.uom_categ_wtime"),
        store=False,
        help="Internal: Only use to filter UoM for Income",
    )
