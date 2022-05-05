#  Copyright (c) 2021 Piruin P.

import math

import pytz

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


def float_time_convert(float_val):
    factor = float_val < 0 and -1 or 1
    val = abs(float_val)
    return factor * int(math.floor(val)), int(round((val % 1) * 60))


def float_time_format(float_val):
    h, m = float_time_convert(float_val)
    return "%0d:%02d" % (h, m)


def _tz_get(self):
    return [
        (tz, tz)
        for tz in sorted(
            pytz.all_timezones, key=lambda tz: tz if not tz.startswith("Etc/") else "_"
        )
    ]


# TODO: migrate to nirun_timing on version 14.0


class Timing(models.Model):
    _name = "ni.timing"
    _description = "Timing"

    name = fields.Char(compute="_compute_name", readonly=False, store=True)
    res_model = fields.Char("Related Document Model", copy=False)
    res_id = fields.Many2oneReference(
        "Related Document ID", model_field="res_model", copy=False
    )
    template_id = fields.Many2one(
        "ni.timing.template", string="Template", required=False, index=True
    )
    bound_start = fields.Datetime("Since", tracking=True, index=True)
    bound_end = fields.Datetime("Until", tracking=True, index=True)
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
    time_of_day = fields.One2many("ni.timing.tod", "timing_id")

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
                    rec.period_text,
                    rec.day_of_week_text,
                    rec.when_text,
                    rec.duration_text,
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
                ("res_model", "=", False),
                ("res_id", "=", False),
                ("create_date", "<", limit_date),
                ("write_date", "<", limit_date),
            ]
        ).unlink()


class TimingTimeOfDay(models.Model):
    _name = "ni.timing.tod"
    _description = "Time of Day"
    timing_id = fields.Many2one("ni.timing", required=True)

    name = fields.Char(store=True, compute="_compute_name")
    code_id = fields.Many2one("ni.timing.tod.code", store=False)
    all_day = fields.Boolean()
    start_time = fields.Float()
    end_time = fields.Float()
    tz = fields.Selection(
        _tz_get, string="Timezone", default=lambda self: self._context.get("tz")
    )
    start = fields.Char(compute="_compute_start_end")
    end = fields.Char(compute="_compute_start_end")

    @api.depends("start_time", "end_time")
    def _compute_start_end(self):
        for rec in self:
            rec.start = float_time_format(rec.start_time)
            rec.end = float_time_format(rec.end_time)

    @api.onchange("all_day", "start_time", "end_time")
    @api.depends("all_day", "start_time", "end_time")
    def _compute_name(self):
        for rec in self:
            if rec.all_day:
                rec.name = _("24 hrs")
                continue
            res = []
            if rec.start_time:
                res.append(rec.start)
                if rec.end_time:
                    res.append(rec.end)
            rec.name = "-".join(res).strip()

    @api.onchange("code_id")
    def onchange_code_id(self):
        if self.code_id:
            data = self.code_id.copy_data()[0]
            field = ["all_day", "start_time", "end_time"]
            self.write({f: data[f] for f in field})


class TimingTimeOfDayCode(models.Model):
    _name = "ni.timing.tod.code"
    _description = "Time of Day Coding"
    _inherit = ["ni.timing.tod", "coding.base"]

    timing_id = fields.Many2one("ni.timing", required=False, store=False)


class TimingDayOfWeek(models.Model):
    _name = "ni.timing.dow"
    _description = "Day of Week"
    _inherit = ["coding.base"]


class TimingEvent(models.Model):
    _name = "ni.timing.event"
    _description = "Timing Event"
    _inherit = ["coding.base"]


class TimingTemplate(models.Model):
    _name = "ni.timing.template"
    _description = "Timing Template"
    _inherit = ["coding.base", "ni.timing"]

    sequence = fields.Integer(copy=False)
    definition = fields.Text(copy=False)
    color = fields.Integer(copy=False)
    active = fields.Boolean(copy=False)

    name = fields.Char("Template Name", compute=None, store=True, copy=False)
    when = fields.Many2many(
        "ni.timing.event", "ni_timing_template_event_rel", "template_id", "event_id"
    )
    day_of_week = fields.Many2many(
        "ni.timing.dow", "ni_timing_template_dow_rel", "template_id", "dow_id"
    )

    def to_timing(self, default=None):
        self.ensure_one()
        vals = self.copy_data(default)
        return self.env["ni.timing"].create(vals)


class TimingMixin(models.AbstractModel):
    _name = "ni.timing.mixin"
    _description = "Timing"

    timing_id = fields.Many2one(
        "ni.timing",
        auto_join=True,
        ondelete="set null",
        tracking=True,
        domain=[
            ("res_model", "=", lambda self: self._name),
            ("res_id", "=", lambda self: self.id),
        ],
    )
    timing_tmpl_id = fields.Many2one("ni.timing.template", store=False)
    timing_when = fields.Many2many(related="timing_id.when")
    timing_dow = fields.Many2many(related="timing_id.day_of_week")
    timing_tod = fields.One2many(related="timing_id.time_of_day")

    @api.model
    def create(self, vals):
        if vals.get("timing_tmpl_id") and not vals.get("timing_id"):
            tmpl = self._get_timing_tmpl(vals.get("timing_tmpl_id"))
            vals["timing_id"] = tmpl.to_timing().ids[0]

        record = super(TimingMixin, self).create(vals)

        if record.timing_id:
            record.timing_id.write({"res_model": record._name, "res_id": record.id})
        return record

    def write(self, vals):
        timing_tmpl = vals.get("timing_tmpl_id") and not vals.get("timing_id")
        if len(self) == 1 and timing_tmpl:
            # if update only one record it easily done
            tmpl = self._get_timing_tmpl(vals.get("timing_tmpl_id"))
            vals["timing_id"] = tmpl.to_timing(
                {"res_model": self._name, "res_id": self.id}
            ).ids[0]
            return super(TimingMixin, self).write(vals)

        success = super(TimingMixin, self).write(vals)
        if timing_tmpl:
            # create timing record for each record that were write
            tmpl = self._get_timing_tmpl(vals.get("timing_tmpl_id"))
            for rec in self:
                rec.timing_id = tmpl.to_timing(
                    {"res_model": rec._name, "res_id": rec.id}
                ).ids[0]
        return success

    def _get_timing_tmpl(self, ids):
        return self.env["ni.timing.template"].browse(ids)

    def unlink(self):
        """Override unlink to delete timing. This cannot be
        cascaded, because link is done through (res_model, res_id)."""
        if not self:
            return True
        self.env["ni.timing"].search(
            [("res_model", "=", self._name), ("res_id", "in", self.ids)]
        ).sudo().unlink()
        return super(TimingMixin, self).unlink()
