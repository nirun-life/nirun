#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import date_utils


class Timing(models.Model):
    _name = "ni.timing"
    _description = "Timing"

    name = fields.Char(compute="_compute_name", readonly=False, store=True)
    bound_start = fields.Datetime("Since", tracking=True, index=True)
    bound_end = fields.Datetime("Until", tracking=True, index=True)
    bound_duration_days = fields.Integer(
        "Duration (Days)",
        compute="_compute_bound_duration",
        inverse="_inverse_bound_duration",
        readonly=False,
        store=True,
    )
    count = fields.Integer("times")
    count_max = fields.Integer("times (max)")

    duration = fields.Integer()
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

    day_of_week = fields.One2many("ni.timing.dow", "timing_id")

    frequency = fields.Integer()
    frequency_max = fields.Integer()
    period = fields.Integer()
    period_max = fields.Integer()
    period_unit = fields.Selection(
        [
            ("year", "Year"),
            ("month", "Month"),
            ("week", "Week"),
            ("day", "Day"),
            ("hour", "Hour"),
            ("minute", "Minute"),
            ("second", "Second"),
        ],
        required=False,
    )
    offset = fields.Integer("", help="Minutes from event (when)")
    when = fields.Many2many(
        "ni.timing.event", "ni_timing_event_rel", "timing_id", "event_id"
    )
    time_of_day = fields.One2many("ni.timing.tod", "timing_id")
    template_id = fields.Many2one(
        "ni.timing.template", string="Template", required=False, index=True
    )

    @api.depends("frequency", "frequency_max", "period", "period_max", "period_unit")
    def _compute_name(self):
        for rec in self:
            text = filter(
                None,
                [
                    rec.frequency_text,
                    rec.period_text,
                    rec.day_of_week_text,
                    rec.when_text,
                    rec.duration_text,
                ],
            )
            rec.name = (" ".join(text)).strip().capitalize()

    @property
    def frequency_text(self):
        if self.frequency == 1 and not self.frequency_max:
            return ""
        if self.frequency > 1 and not self.frequency_max:
            return _("%s times") % self.frequency
        if self.frequency and self.frequency_max:
            return _("%s-%s times") % (self.frequency, self.frequency_max)

    @property
    def period_text(self):
        if self.period == 1 and not self.period_max:
            return (
                _("every %s") % self.period_unit
                if not (self.period_unit == "day" and self.day_of_week)
                else ""
            )
        if self.period > 1 and not self.period_max:
            return _("every %s %ss") % (self.period, self.period_unit_text.lower())
        if self.period and self.period_max:
            return _("every %s-%s %ss") % (
                self.period,
                self.period_max,
                self.period_unit_text.lower(),
            )
        else:
            return ""

    @property
    def day_of_week_text(self):
        dow = self.day_of_week.mapped("value")
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
    def period_unit_text(self):
        return dict(self._fields["period_unit"].selection).get(self.period_unit)

    @property
    def duration_unit_text(self):
        return dict(self._fields["duration_unit"].selection).get(self.duration_unit)

    @property
    def duration_text(self):
        if self.duration and not self.duration_max:
            return _("for %s %s") % (self.duration, self.duration_unit_text)
        if self.duration and self.duration_max:
            return _("for %s-%s %s") % (
                self.duration,
                self.duration_max,
                self.duration_unit_text,
            )
        else:
            return ""

    @api.onchange("bound_start", "bound_end")
    def _compute_bound_duration(self):
        for rec in self:
            rec.duration_days = 0
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


class TimingTimeOfDay(models.Model):
    _name = "ni.timing.tod"
    _description = "Time of Day"
    timing_id = fields.Many2one("ni.timing", required=True)
    value = fields.Float()


class TimingDayOfWeek(models.Model):
    _name = "ni.timing.dow"
    _description = "Day of Week"
    timing_id = fields.Many2one("ni.timing", required=True)
    value = fields.Selection(
        [
            ("Mon", "Monday"),
            ("Tue", "Tuesday"),
            ("Wed", "Wednesday"),
            ("Thu", "Thursday"),
            ("Fri", "Friday"),
            ("Sat", "Saturday"),
            ("Sun", "Sunday"),
        ],
        required=True,
    )

    _sql_constraints = [
        (
            "timing_value__uniq",
            "unique (timing_id, value)",
            "Duplicate day of week in timing!",
        ),
    ]


class TimingEvent(models.Model):
    _name = "ni.timing.event"
    _description = "Timing Event"
    _inherit = ["coding.base"]


class TimingTemplate(models.Model):
    _name = "ni.timing.template"
    _description = "Timing Template"
    _inherit = ["coding.base", "ni.timing"]

    name = fields.Char("Template Name", compute=None, store=True)
    when = fields.Many2many(
        "ni.timing.event", "ni_timing_template_event_rel", "template_id", "event_id"
    )
