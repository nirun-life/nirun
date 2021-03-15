#  Copyright (c) 2021 Piruin P.

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PeriodMixin(models.AbstractModel):
    _name = "period.mixin"
    _description = "Period Mixin"

    _date_name = "period_start"
    period_start = fields.Date(
        tracking=True, index=True, default=lambda self: fields.Date.context_today(self)
    )
    period_end = fields.Date(tracking=True, index=True)
    duration = fields.Char("Duration", compute="_compute_duration", default="")
    duration_days = fields.Integer(
        "Duration (days)", compute="_compute_duration", default=0
    )
    duration_months = fields.Integer(
        "Duration (months)", compute="_compute_duration", default=0
    )
    duration_years = fields.Integer(
        "Duration (years)", compute="_compute_duration", default=0
    )

    @api.onchange("period_start", "period_end")
    def _compute_duration(self):
        today = fields.Date.context_today(self)
        for record in self:
            record.duration_years = 0
            record.duration_months = 0
            record.duration_days = 0
            record.duration = ""
            if record.period_start:
                dt = record.period_end or today
                delta = dt - record.period_start
                record.duration_days = delta.days
                record.duration_months = delta.days / 30
                delta = relativedelta(dt, record.period_start)
                record.duration_years = delta.years
                record.duration = record._format_relative_delta(delta)

    @api.model
    def _format_relative_delta(self, delta):
        result = []
        if delta.years > 0:
            result.append(_("%s Years") % delta.years)
        if delta.months > 0:
            result.append(_("%s Months") % delta.months)
        if delta.days > 0:
            result.append(_("%s Days") % delta.days)
        if delta.days < 0:
            result.append(_("Next %s days") % abs(delta.days))
        return " ".join(result) or None

    @api.constrains("period_start", "period_end")
    def _check_end_date(self):
        for record in self:
            if not record.period_end or not record.period_start:
                continue
            if record.period_end < record.period_start:
                raise ValidationError(
                    _("End date should not set before start date (%s)")
                    % self.period_start
                )
