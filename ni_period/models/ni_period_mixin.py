#  Copyright (c) 2021-2023 NSTDA
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PeriodMixin(models.AbstractModel):
    _name = "ni.period.mixin"
    _description = "Period"
    _workflow_occurrence_field = "period_start"

    period_mode = fields.Selection(
        [("datetime", "Date / Time"), ("date", "Date")],
        "Period",
        default="datetime",
        required=True,
    )
    period_start = fields.Datetime(
        "Since", index=True, default=lambda self: fields.Datetime.now()
    )
    period_start_date = fields.Date(
        "Since (Date)",
        index=True,
        readonly=False,
        store=True,
        compute="_compute_period_start_date",
        inverse="_inverse_period_start_date",
        default=lambda self: fields.Date.context_today(self),
    )
    period_end = fields.Datetime(
        "Until",
        compute="_compute_period_end",
        store=True,
        readonly=False,
        index=True,
    )
    period_end_date = fields.Date(
        "Until (Date)",
        index=True,
        readonly=False,
        store=True,
        compute="_compute_period_end_date",
        inverse="_inverse_period_end_date",
    )
    period_end_date_calendar = fields.Date(compute="_compute_period_end_date_calendar")
    duration = fields.Char(
        "Duration",
        compute="_compute_duration",
        default="",
    )
    duration_hours = fields.Float(
        "Duration (Hours)", compute="_compute_duration", readonly=False, default=0.0
    )
    duration_days = fields.Integer(
        "Duration (days)",
        compute="_compute_duration",
        default=0,
    )
    duration_months = fields.Integer(
        "Duration (months)",
        compute="_compute_duration",
        default=0,
    )
    duration_years = fields.Integer(
        "Duration (years)",
        compute="_compute_duration",
        default=0,
    )
    tense = fields.Selection(
        [("past", "Past"), ("present", "Present"), ("future", "Future")],
        compute="_compute_tense",
        required=False,
        readonly=True,
    )
    is_present = fields.Boolean(compute="_compute_tense", readonly=True)
    is_past = fields.Boolean(compute="_compute_tense", readonly=True)
    is_future = fields.Boolean(compute="_compute_tense", readonly=True)

    @api.depends("period_start")
    def _compute_period_start_date(self):
        for rec in self:
            if rec.period_start:
                rec.period_start_date = rec.period_start.date()

    def _inverse_period_start_date(self):
        for rec in self:
            if rec.period_start_date and not rec.period_start:
                dt = fields.Datetime.from_string(rec.period_start_date)
                dt = dt.replace(hour=0, tzinfo=None)
                rec.period_start = dt

    @api.depends("period_end")
    def _compute_period_end_date(self):
        for rec in self:
            if rec.period_end:
                rec.period_end_date = rec.period_end.date()

    def _inverse_period_end_date(self):
        for rec in self:
            if rec.period_end_date and not rec.period_end:
                dt = fields.Datetime.from_string(rec.period_end_date)
                dt = dt.replace(hour=0, tzinfo=None)
                rec.period_end = dt

    @api.onchange("period_start_date", "period_end_date")
    @api.depends("period_start_date", "period_end_date")
    def _compute_tense(self):
        today = fields.Date.today()
        for rec in self:
            is_present = rec.in_period(today)
            is_past = rec.period_end_date and today > rec.period_end_date
            is_future = rec.period_start_date and today < rec.period_start_date
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
        if not self.period_start_date and not self.period_end_date:
            return False
        if self.period_start_date and date < self.period_start_date:
            return False
        if self.period_end_date and date > self.period_end_date:
            return False
        return True

    @api.depends("period_start", "duration_hours")
    def _compute_period_end(self):
        self.env.remove_to_compute(self._fields["duration_years"], self)
        self.env.remove_to_compute(self._fields["duration_months"], self)
        self.env.remove_to_compute(self._fields["duration_days"], self)
        self.env.remove_to_compute(self._fields["duration_hours"], self)
        self.env.remove_to_compute(self._fields["duration"], self)
        for rec in self:
            if rec.period_start and rec.duration_hours:
                rec.period_end = rec.period_start and rec.period_start + timedelta(
                    minutes=round((rec.duration_hours or 1.0) * 60)
                )

    @api.depends("period_start", "period_end")
    def _compute_duration(self):
        now = fields.Datetime.now()
        self.env.remove_to_compute(self._fields["period_end"], self)
        for rec in self:
            data = {
                "duration_years": 0,
                "duration_months": 0,
                "duration_days": 0,
                "duration_hours": self._get_duration_hours(
                    rec.period_start, rec.period_end
                ),
                "duration": None,
            }
            if rec.period_start:
                dt = rec.period_end if rec.period_end else now
                delta = relativedelta(dt, rec.period_start)
                data["duration_days"] = delta.days
                data["duration_months"] = delta.months
                data["duration_years"] = delta.years
                data["duration"] = rec._format_relative_delta(delta)
            rec.update(data)

    def _get_duration_hours(self, start, stop):
        if not start or not stop:
            return 0.0
        duration = (stop - start).total_seconds() / 3600
        return round(duration, 2)

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
            if not self.period_end:
                result.append(_("Today"))
            else:
                if delta.hours > 0:
                    result.append(_("%s Hours") % delta.hours)
                if delta.minutes > 0:
                    result.append(_("%s Minutes") % delta.minutes)
                if not result:
                    result.append(_("%s Seconds") % delta.seconds)
        if delta.days < 0:
            result.append(_("Next %s days") % abs(delta.days))
        return " ".join(result) or None

    @api.constrains("period_start_date", "period_end_date")
    def _check_end_date(self):
        for record in self:
            if not record.period_end_date or not record.period_start_date:
                continue
            if record.period_end_date < record.period_start_date:
                raise ValidationError(
                    _("(%s), End date (%s) should not set before start date (%s)")
                    % (
                        record._description,
                        record.period_end_date,
                        record.period_start_date,
                    )
                )

    def get_intercept_period(self, start, end, domain):
        args = [
            ("period_start", "<=", end or start),
            "|",
            ("period_end", "=", False),
            ("period_end", ">=", start),
        ]
        if domain:
            args += domain
        return self.env[self._name].search(args)

    def search_intercept(self, domain=None):
        self.ensure_one()
        domain = domain or []
        domain += [("id", "!=", self.id)]
        return self.get_intercept_period(self.period_start, self.period_end, domain)

    @api.depends("period_start_date", "period_start_date")
    def _compute_period_end_date_calendar(self):
        for rec in self:
            # adding 1 days because calendar view's date_stop is exclusive date
            rec.period_end_date_calendar = (
                rec.period_start_date or fields.Date.context_today(self)
            ) + relativedelta(days=1)
