#  Copyright (c) 2021-2023 NSTDA

from odoo import _, _lt, api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools import date_utils

time_unit = {
    "year": _lt("year"),
    "month": _lt("month"),
    "week": _lt("week"),
    "day": _lt("day"),
    "hour": _lt("hour"),
    "minute": _lt("minute"),
    "second": _lt("second"),
}

time_unit_plural = {
    "year": _lt("years"),
    "month": _lt("months"),
    "week": _lt("weeks"),
    "day": _lt("days"),
    "hour": _lt("hours"),
    "minute": _lt("minutes"),
    "second": _lt("seconds"),
}


class Timing(models.Model):
    _name = "ni.timing.timing"
    _description = "Timing"

    name = fields.Text(compute="_compute_name", readonly=False, store=True)
    code = fields.Char(help="Store when apply template but may not always consistency")
    res_model = fields.Char("Related Document Model", copy=False)
    res_id = fields.Many2oneReference(
        "Related Document ID", model_field="res_model", copy=False
    )
    template_id = fields.Many2one(
        "ni.timing.template", string="Template", required=False, index=True
    )
    bound_start = fields.Datetime("Since", index=True)
    bound_end = fields.Datetime("Until", index=True)
    bound_duration_days = fields.Integer(
        "Duration (Days)",
        compute="_compute_bound_duration",
        inverse="_inverse_bound_duration",
        readonly=False,
        store=True,
    )

    frequency = fields.Integer(
        default=1, help="Event occurs frequency times per period"
    )
    frequency_max = fields.Integer()
    duration = fields.Integer(help="How long when it happens")
    duration_max = fields.Integer()
    duration_unit = fields.Selection(
        [
            ("year", "Years"),
            ("month", "Months"),
            ("week", "Weeks"),
            ("day", "Days"),
            ("hour", "Hours"),
            ("minute", "Minutes"),
            ("second", "Seconds"),
        ],
        required=False,
    )

    repeat_type = fields.Selection(
        [("period", "Period"), ("dow", "Day of Week")], default="period"
    )
    period = fields.Integer(default=1)
    period_max = fields.Integer()
    period_unit = fields.Selection(
        [
            ("year", "Years"),
            ("month", "Months"),
            ("week", "Weeks"),
            ("day", "Days"),
            ("hour", "Hours"),
            ("minute", "Minutes"),
            ("second", "Seconds"),
        ],
        required=False,
        default="day",
    )
    everyday = fields.Boolean(readonly=False, compute="_compute_everyday")
    day_of_week = fields.Many2many(
        "ni.timing.dow", "ni_timing_dow_rel", "timing_id", "dow_id"
    )
    time_type = fields.Selection(
        [("event", "Event"), ("tod", "Time of Day")], default="event"
    )
    offset = fields.Integer("", help="Minutes from event (before of after)")
    when = fields.Many2many(
        "ni.timing.event",
        "ni_timing_event_rel",
        "timing_id",
        "event_id",
        auto_join=True,
    )
    time_of_day = fields.One2many("ni.timing.timing.tod", "timing_id")

    def init(self):
        tools.create_index(
            self._cr, "ni_timing_res_model_id_idx", self._table, ["res_model", "res_id"]
        )

    @api.depends(
        "frequency",
        "frequency_max",
        "duration",
        "duration_max",
        "duration_unit",
        "period",
        "period_max",
        "period_unit",
        "day_of_week",
        "when",
        "offset",
    )
    @api.onchange(
        "frequency",
        "frequency_max",
        "duration",
        "duration_max",
        "duration_unit",
        "period",
        "period_max",
        "period_unit",
        "day_of_week",
        "when",
        "offset",
    )
    def _compute_name(self):
        for rec in self:
            text = filter(
                None,
                [
                    rec.frequency_text,
                    rec.duration_text,
                    rec.period_text,
                    "at" if rec.time_of_day_text else "",
                    rec.time_of_day_text,
                    rec.day_of_week_text,
                    rec.when_text,
                ],
            )
            rec.name = (" ".join(text)).strip().capitalize()

    @api.onchange("period_unit")
    def _onchange_period_unit(self):
        if self.period_unit != "week" and self.day_of_week:
            self.update({"day_of_week": [(5, 0, 0)]})

    @api.onchange("template_id")
    def _onchange_template(self):
        if self.template_id:
            self.update(
                {
                    "frequency": self.template_id.frequency,
                    "frequency_max": self.template_id.frequency_max,
                    "duration": self.template_id.duration,
                    "duration_max": self.template_id.duration_max,
                    "duration_unit": self.template_id.duration_unit,
                    "period": self.template_id.period,
                    "period_max": self.template_id.period_max,
                    "period_unit": self.template_id.period_unit,
                    "when": [(6, 0, self.template_id.when.ids)],
                    "day_of_week": [(6, 0, self.template_id.day_of_week.ids)],
                    "offset": self.template_id.offset,
                    "time_of_day": [(6, 0, self.template_id.time_of_day.ids)],
                    "name": self.template_id.name,
                }
            )

    @api.onchange("everyday")
    def _onchange_everyday(self):
        all_dow = self.env["ni.timing.dow"].search([]).mapped("id")
        for rec in self:
            org = rec._origin
            if not org.everyday and rec.everyday:
                rec.day_of_week = [(6, 0, all_dow)]

    @api.onchange("day_of_week")
    @api.depends("day_of_week")
    def _compute_everyday(self):
        for rec in self:
            rec.everyday = len(rec.day_of_week) == 7

    @property
    def frequency_text(self):
        if self.frequency == 1 and (not self.frequency_max or self.frequency_max == 1):
            return ""
        if self.frequency > 1 and (
            not self.frequency_max or self.frequency == self.frequency_max
        ):
            return _("%s times") % self.frequency
        if self.frequency and self.frequency_max:
            return _("%s-%s times") % (self.frequency, self.frequency_max)

    @property
    def period_text(self):
        if self.period == 1 and (not self.period_max or self.period_max == 1):
            return (
                _("every %s") % time_unit.get(self.period_unit)
                if not (self.period_unit == "week" and self.day_of_week)
                else ""
            )
        if self.period > 1 and (not self.period_max or self.period == self.period_max):
            return _("every %s %s") % (
                self.period,
                time_unit_plural.get(self.period_unit),
            )
        if self.period and self.period_max:
            return _("every %s-%s %s") % (
                self.period,
                self.period_max,
                time_unit_plural.get(self.period_unit),
            )
        else:
            return ""

    @property
    def day_of_week_text(self):
        if self.everyday:
            return "Everyday"
        dow = self.day_of_week.mapped("name")
        return ", ".join(dow) if dow else ""

    @property
    def when_text(self):
        wh = self.when.sorted("code").mapped("name")
        return (
            ", ".join(wh)
            if not self.offset
            else _("%s min %s") % (self.offset, ", ".join(wh))
        )

    @property
    def duration_text(self):
        if self.duration and (
            not self.duration_max or self.duration_max == self.duration
        ):
            return _("for %s %s") % (
                self.duration,
                time_unit.get(self.duration_unit)
                if self.duration == 1
                else time_unit_plural.get(self.duration_unit),
            )
        if self.duration and self.duration_max:
            return _("for %s-%s %s") % (
                self.duration,
                self.duration_max,
                time_unit_plural.get(self.duration_unit),
            )
        else:
            return ""

    @property
    def time_of_day_text(self):
        tod = self.time_of_day.mapped("name")
        return ", ".join(tod) if tod else ""

    @api.onchange("bound_start", "bound_end")
    def _compute_bound_duration(self):
        for rec in self:
            if rec.bound_start and rec.bound_end:
                if rec.bound_start > rec.bound_end:
                    return {
                        "warning": {
                            "title": ("warning"),
                            "message": ("bound end should should be more than start"),
                        }
                    }
                delta = rec.bound_end - rec.bound_start
                rec.bound_duration_days = delta.days
            else:
                rec.bound_duration_days = 0

    @api.onchange("bound_duration_days")
    def _inverse_bound_duration(self):
        for rec in self:
            if rec.bound_end and not rec.bound_start:
                rec.bound_start = date_utils.add(
                    rec.bound_end, days=rec.bound_duration_days
                )
            elif rec.bound_start:
                rec.bound_end = date_utils.add(
                    rec.bound_start, days=rec.bound_duration_days
                )

    @api.constrains("time_of_day", "when", "offset")
    def check_timeofday_when(self):
        for rec in self:
            if rec.offset and (not rec.when or rec.is_with_meal):
                raise ValidationError(
                    _(
                        "If there's an offset, there must be a when "
                        "(and not C, CM, CD, CV)"
                    )
                )
            if rec.time_of_day and rec.when:
                raise ValidationError(
                    _("If there's a time_of_day, there cannot be a when, or vice versa")
                )

    @property
    def is_with_meal(self):
        with_meal_when = ["C", "CM", "CD", "CV"]
        return any([when in with_meal_when for when in self.when.mapped("code")])

    @api.constrains("duration", "duration_max")
    def check_duration(self):
        for rec in self:
            if rec.duration and not rec.duration_unit:
                raise ValidationError(
                    _("If there's a duration, there needs to be duration units")
                )
            if rec.duration < 0:
                raise ValidationError(_("duration SHALL be a non-negative value"))
            if rec.duration_max and not rec.duration:
                raise ValidationError(
                    _("If there's a durationMax, there must be a duration")
                )
            if rec.duration_max and rec.duration > rec.duration_max:
                raise ValidationError(
                    _("duration max must be more than min [%s]") % rec.duration
                )

    @api.constrains("frequency", "frequency_max")
    def check_frequency(self):
        for rec in self:
            if rec.frequency < 0:
                raise ValidationError(_("frequency SHALL be a non-negative value"))
            if rec.frequency_max and not rec.frequency:
                raise ValidationError(
                    _("If there's a frequencyMax, there must be a frequency")
                )
            if rec.frequency_max and rec.frequency > rec.frequency_max:
                raise ValidationError(
                    _("frequency max must be more than min [%s]") % rec.frequency
                )

    @api.constrains("period", "period_max")
    def check_period(self):
        for rec in self:
            if rec.period and not rec.period_unit:
                raise ValidationError(
                    _("If there's a period, there needs to be period units")
                )
            if rec.period < 0:
                raise ValidationError(_("period SHALL be a non-negative value"))
            if rec.period_max and not rec.period:
                raise ValidationError(
                    _("If there's a periodMax, there must be a period")
                )
            if rec.period_max and rec.period > rec.period_max:
                raise ValidationError(
                    _("period max must be more than min [%s]") % rec.period
                )

    @api.model
    def garbage_collect(self):
        from odoo.tools.date_utils import get_timedelta

        limit_date = fields.datetime.utcnow() - get_timedelta(1, "day")

        return self.search(
            [
                "|",
                ("res_model", "=", False),
                ("res_id", "=", False),
                ("create_date", "<", limit_date),
                ("write_date", "<", limit_date),
            ]
        ).unlink()
