#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    period_start_year_be = fields.Integer(
        "Since Year (BE)",
        compute="_compute_period_start_year_be",
        inverse="_inverse_period_start_year_be",
        store=True,
        default=None,
    )

    @api.onchange("period_start")
    def _onchange_period_start(self):
        if self.period_start and self.period_start_year_be != (
            self.period_start.year + 543
        ):
            self.period_start_year_be = self.period_start.year + 543

    @api.depends("period_start")
    def _compute_period_start_year_be(self):
        for rec in self:
            rec._onchange_period_start()

    @api.onchange("period_start_year_be")
    def _onchange_period_start_year_be(self):
        if self.period_start_year_be and (
            not self.period_start
            or self.period_start.year != self.period_start_year_be - 543
        ):
            if self.period_start_year_be < 1900 + 543:
                return {
                    "warning": {
                        "title": _("Error"),
                        "message": _("System does not support date before 1900-01-01"),
                    },
                    "value": {"period_start_year_be": 1900 + 543},
                }
            self._inverse_period_start_year_be()

    def _inverse_period_start_year_be(self):
        today = fields.date.today().replace(month=1, day=1)
        for rec in self:
            if not rec.period_start_year_be:
                continue
            base = rec.period_start or today
            date = "{}-{}-{}".format(
                rec.period_start_year_be - 543, base.month, base.day
            )
            rec.period_start = fields.Date.to_date(date)
