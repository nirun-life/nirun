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
    tense = fields.Selection(
        [("past", "Past"), ("present", "Present"), ("future", "Future")],
        compute="_compute_tense",
        require=False,
        readonly=True,
    )
    is_present = fields.Boolean(compute="_compute_tense", readonly=True)
    is_past = fields.Boolean(compute="_compute_tense", readonly=True)
    is_future = fields.Boolean(compute="_compute_tense", readonly=True)

    @api.onchange("period_start", "period_end")
    @api.depends("period_start", "period_end")
    def _compute_tense(self):
        today = fields.Date.today()
        for rec in self:
            is_present = rec.in_period(today)
            is_past = rec.period_end and today > rec.period_end
            is_future = rec.period_start and today < rec.period_start
            rec.update(
                {
                    "is_present": is_present,
                    "is_past": is_past,
                    "is_future": is_future,
                    "tense": (
                        "present"
                        if is_present
                        else "past"
                        if is_past
                        else "future"
                        if is_future
                        else None
                    ),
                }
            )

    def in_period(self, date=None):
        self.ensure_one()
        if not date:
            date = fields.Date.today()
        if not self.period_start and not self.period_end:
            return False
        if self.period_start and date < self.period_start:
            return False
        if self.period_end and date > self.period_end:
            return False
        return True

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
        if delta.days == 0 and not result:
            result.append(_("Today"))
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
