#  Copyright (c) 2021 Piruin P.
import datetime

import pytz

from odoo import api, fields, models


def naive_utc(value, timezone):
    naive_datetime = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M")
    local_datetime = timezone.localize(naive_datetime, is_dst=None)
    utc_time = local_datetime.astimezone(pytz.utc)
    return str(utc_time)[0:-6]


class HealthcareServiceTime(models.Model):
    _inherit = "ni.service.time"

    def get_calendar_dict(self, start_date):
        self.ensure_one()
        start_datetime = fields.Datetime.to_datetime(start_date)
        res = {
            "interval": 1,
            "rrule_type": "weekly",
            "allday": self.all_day,
            "start": start_datetime,
            "stop": start_datetime,
        }

        if not self.all_day:
            tz = self._get_timezone()
            start_time = "{} {}".format(start_date, self.start)
            stop_time = "{} {}".format(start_date, self.end)
            res.update(
                {
                    "start": fields.Datetime.to_datetime(naive_utc(start_time, tz)),
                    "stop": fields.Datetime.to_datetime(naive_utc(stop_time, tz)),
                }
            )

        res.update(self._get_day_of_week_calendar_dict())
        return res

    def _get_timezone(self):
        if self.tz:
            return pytz.timezone(self.tz)
        if self.env.user.tz:
            return pytz.timezone(self.env.user.tz)
        return pytz.utc

    def _get_day_of_week_calendar_dict(self):
        self.ensure_one()
        res = {}
        for day in self.day_of_week:
            field = day.code[0:2].lower()
            res[field] = True
        return res


class HealthcareServiceTimingCalendarWizard(models.TransientModel):
    _name = "ni.service.time.schedule"
    _description = "Healthcare Service Schedule"
    _inherit = ["period.mixin"]

    service_id = fields.Many2one("ni.service", required=True)
    time_id = fields.Many2one("ni.service.time", required=True)
    partner_ids = fields.Many2many(
        "res.partner", string="Participant", compute="_compute_partner_ids"
    )
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)

    @api.onchange("period_start")
    def onchange_period_start(self):
        if not self.period_end or self.period_end < self.period_start:
            self.period_end = self.period_start

    @api.depends("period_start", "period_end")
    def _compute_partner_ids(self):
        # FIXME remove participant from event that not on their request period
        for rec in self:
            request = self.env["ni.service.request"].get_intercept_period(
                rec.period_start, rec.period_end, domain=[("state", "in", ["active"])]
            )
            if request:
                rec.partner_ids = request.mapped("partner_id")
            else:
                rec.partner_ids = [(6, 0, [])]

    def schedule(self):
        val = self._get_calendar_dict()
        val.update(self.time_id.get_calendar_dict(self.period_start))
        events = self.env["calendar.event"]
        events.create(val)

        return self.service_id.action_calendar_event()

    def _get_calendar_dict(self):
        self.ensure_one()
        return {
            "res_id": self.service_id.id,
            "res_model": "ni.service",
            "recurrency": True,
            "end_type": "end_date",
            "final_date": self.period_end,
            "name": self.service_id.name,
            "location": self.service_id.location,
            "partner_ids": self.partner_ids,
        }
