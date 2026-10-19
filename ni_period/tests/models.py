#  Copyright (c) 2026 NSTDA

from odoo import fields, models


class PeriodTest(models.Model):
    _name = "ni.period.test"
    _inherit = "ni.period.mixin"
    _description = "Period Test"


class PeriodOwnDateTest(models.Model):
    _name = "ni.period.own.date.test"
    _inherit = "ni.period.mixin"
    _description = "Period Test (own start date)"

    period_start_date = fields.Date(
        default=None,
        compute="_compute_period_start_date",
        inverse="_inverse_period_start_date",
        store=True,
        readonly=False,
    )
