#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.nirun_service.models.service import float_time_format


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
    start_time = fields.Float()
    end_time = fields.Float()

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
