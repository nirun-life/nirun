#  Copyright (c) 2021 Piruin P.

import math

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


def float_time_convert(float_val):
    factor = float_val < 0 and -1 or 1
    val = abs(float_val)
    return factor * int(math.floor(val)), int(round((val % 1) * 60))


def float_time_format(float_val):
    h, m = float_time_convert(float_val)
    return "%0d:%02d" % (h, m)


class HealthcareServiceCategory(models.Model):
    _name = "ni.service.category"
    _description = "Healthcare Service Category"
    _inherit = ["coding.base"]


class HealthcareServiceAvailableTime(models.Model):
    _name = "ni.service.time"
    _description = "Healthcare Service Available Time"

    service_id = fields.Many2one("ni.service", ondelete="cascade")
    name = fields.Char(compute="_compute_name", store=True)

    everyday = fields.Boolean(readonly=False, compute="_compute_everyday")
    day_of_week = fields.Many2many(
        "ni.timing.dow", "ni_service_time_dow", "timing_id", "dow_id"
    )
    all_day = fields.Boolean()
    start_time = fields.Integer()
    end_time = fields.Integer()

    display_day = fields.Char("Day", compute="_compute_dow_txt")
    display_time = fields.Char("Time", compute="_compute_time_txt")

    @api.depends("day_of_week", "all_day", "start_time", "end_time")
    def _compute_name(self):
        for rec in self:
            text = filter(None, [rec.display_day, rec.display_time])
            rec.name = (" ".join(text)).strip().capitalize()

    @api.onchange("start_time")
    def _onchange_start_time(self):
        if self._origin.start_time == self._origin.end_time:
            self.end_time = self.start_time
        if self.end_time < self.start_time:
            self.end_time = self.start_time

    @api.depends("day_of_week")
    def _compute_dow_txt(self):
        for rec in self:
            dow = rec.day_of_week.mapped("name")
            rec.display_day = ", ".join(dow) if dow else ""

    @api.depends("all_day", "start_time", "end_time")
    def _compute_time_txt(self):
        for rec in self:
            if rec.all_day:
                rec.display_time = _("24 hrs")
                continue
            res = []
            if rec.start_time:
                res.append(float_time_format(rec.start_time))
                if rec.end_time:
                    res.append(float_time_format(rec.end_time))
            rec.display_time = "-".join(res).strip()

    def check_end_time(self):
        for rec in self:
            if not rec.all_day and rec.end_time < rec.start_time:
                raise ValidationError(_("End time must be set after start time"))

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


class HealthcareServiceTiming(models.Model):
    _name = "ni.service.timing"
    _description = "Healthcare Service Event Timing"
    _inherit = ["ni.timing"]

    service_id = fields.Many2one("ni.service", ondelete="cascade")

    day_of_week = fields.Many2many(
        "ni.timing.dow", "ni_service_timing_dow", "timing_id", "dow_id"
    )
    when = fields.Many2many(
        "ni.timing.event",
        "ni_service_timing_event",
        "timing_id",
        "event_id",
        auto_join=True,
    )


class HealthcareService(models.Model):
    _name = "ni.service"
    _description = "Healthcare Service"
    _inherit = ["mail.thread", "image.mixin", "coding.base"]

    company_id = fields.Many2one(
        "res.company",
        "Company",
        tracking=True,
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    name = fields.Char(index=True)
    active = fields.Boolean(default=True)
    code = fields.Char("Internal Reference", index=True)
    category_ids = fields.Many2many(
        "ni.service.category",
        "ni_service_category_rel",
        "service_id",
        "category_id",
        help="Broad category of service being performed or delivered",
    )
    location_ids = fields.Many2many(
        "ni.location",
        "ni_service_location",
        "service_id",
        "location_id",
        help="Location(s) where service may be provided",
        ondelete="cascade",
    )
    comment = fields.Text(
        "Internal Notes",
        help="Additional description and/or any specific issues not covered elsewhere",
    )

    available_type = fields.Selection(
        [("routine", "Routine "), ("event", "Event")],
        default="routine",
        required=True,
        help="""Whether service is routine or base on event.
         Technical: time_ids for routine, timing_ids for event""",
    )
    available_time_ids = fields.One2many(
        "ni.service.time",
        "service_id",
        "Available Times",
        help="Times the Service is available",
    )
    available_timing_ids = fields.One2many(
        "ni.service.timing",
        "service_id",
        "Recurrent",
        help="When the Service is to occur",
    )
    condition_ids = fields.Many2many(
        "ni.condition", "ni_service_condition", "service_id", "condition_id"
    )

    request_ids = fields.One2many("ni.service.request", "service_id")


class Condition(models.Model):
    _inherit = "ni.condition"

    service_ids = fields.Many2many(
        "ni.service", "ni_service_condition", "condition_id", "service_id"
    )
