#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models
from odoo.tools.date_utils import end_of, relativedelta, start_of

rrule_map = {"year": "yearly", "month": "monthly", "week": "weekly", "day": "daily"}


class HealthcareServiceTiming(models.Model):
    _inherit = "ni.service.timing"

    event_ids = fields.One2many("calendar.event", "timing_id")
    event_count = fields.Integer(compute="_compute_event_ids", store=True)
    event_final_date = fields.Date(compute="_compute_event_ids", store=True)

    @api.depends("event_ids")
    def _compute_event_ids(self):
        events = (
            self.env["calendar.event"]
            .sudo()
            .read_group(
                [("timing_id", "in", self.ids)],
                ["final_date:max"],
                groupby=["timing_id"],
            )
        )
        data = {res["timing_id"][0]: res["final_date"] for res in events}
        for rec in self:
            rec.event_count = len(rec.event_ids)
            rec.event_final_date = data.get(rec.id, None) if rec.event_count else None

    def get_calendar_dict(self, start_date, final_date=None):
        self.ensure_one()
        start_datetime = fields.Datetime.to_datetime(start_date)
        stop_datetime = self._stop_datetime_for(start_datetime)
        vals = {
            "name": "{} - {}".format(self.service_id.name, self.name),
            "location": self.service_id.location,
            "service_id": self.service_id.id,
            "timing_id": self.id,
            "res_id": self.service_id.id,
            "res_model": "ni.service",
            "start": start_datetime,
            "stop": stop_datetime,
            "privacy": "public",
            "rrule_type": rrule_map[self.period_unit],
            "interval": self.period,
            "recurrency": True,
        }
        if final_date:
            vals.update(
                {
                    "end_type": "end_date",
                    "final_date": final_date,
                }
            )
        if self.period_unit == "week":
            vals.update(self._get_day_of_week_calendar_dict())
        return vals

    def _stop_datetime_for(self, start_datetime):
        duration = {
            "{}s".format(self.duration_unit): self.duration_max or self.duration
        }
        return start_datetime + relativedelta(duration)

    def _get_day_of_week_calendar_dict(self):
        self.ensure_one()
        res = {}
        for day in self.day_of_week:
            field = day.code[0:2].lower()
            res[field] = True
        return res

    @api.model
    def cron_calendar(self):
        next_month = fields.Date.today() + relativedelta(months=1)
        start = start_of(next_month, granularity="month")
        final = end_of(next_month, granularity="month")

        target = self.search(
            ["|", ("event_final_date", "<", start), ("event_final_date", "=", False)]
        )
        events = self.env["calendar.event"]
        events.create([rec.get_calendar_dict(start, final) for rec in target])
