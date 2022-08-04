from datetime import datetime

from pytz import timezone, utc

from odoo import api, fields, models
from odoo.tools.date_utils import end_of, relativedelta, start_of


def naive_utc(value, timezone):
    naive_datetime = datetime.strptime(value, "%Y-%m-%d %H:%M")
    local_datetime = timezone.localize(naive_datetime, is_dst=None)
    utc_time = local_datetime.astimezone(utc)
    return str(utc_time)[0:-6]


class HealthcareServiceTime(models.Model):
    _inherit = "ni.service.time"

    event_ids = fields.One2many("calendar.event", "time_id")
    event_count = fields.Integer(compute="_compute_event_ids", store=True)
    event_final_date = fields.Date(compute="_compute_event_ids", store=True)

    @api.depends("event_ids")
    def _compute_event_ids(self):
        events = (
            self.env["calendar.event"]
            .sudo()
            .read_group(
                [("time_id", "in", self.ids)], ["final_date:max"], groupby=["time_id"]
            )
        )
        data = {res["time_id"][0]: res["final_date"] for res in events}
        for rec in self:
            rec.event_count = len(rec.event_ids)
            rec.event_final_date = data.get(rec.id, None) if rec.event_count else None

    def get_calendar_dict(self, start_date, final_date=None):
        self.ensure_one()
        start_datetime = fields.Datetime.to_datetime(start_date)
        res = {
            "name": self.service_id.name,
            "location": self.service_id.location,
            "service_id": self.service_id.id,
            "time_id": self.id,
            "res_id": self.service_id.id,
            "res_model": "ni.service",
            "recurrency": True,
            "interval": 1,
            "rrule_type": "weekly",
            "allday": self.all_day,
            "start": start_datetime,
            "stop": start_datetime,
        }
        if final_date:
            res.update(
                {
                    "end_type": "end_date",
                    "final_date": final_date,
                }
            )

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
            return timezone(self.tz)
        if self.env.user.tz:
            return timezone(self.env.user.tz)
        return utc

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