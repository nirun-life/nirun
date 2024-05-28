#  Copyright (c) 2024 NSTDA
import pprint
from datetime import date, datetime

from pytz import timezone

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    resource_calendar_id = fields.Many2one(
        "resource.calendar", "ตารางเวลา", check_company=True
    )
    service_ids = fields.Many2many(
        "ni.service", domain="[('company_id', '=', company_id)]"
    )
    service_attendance_ids = fields.One2many(
        "ni.encounter.service.attendance", "encounter_id"
    )

    @api.onchange("class_id")
    def _onchange_class_id(self):
        for rec in self:
            if rec.class_id.service_calendar_id:
                rec.resource_calendar_id = rec.class_id.service_calendar_id

    def action_generate_service_resource(self):
        self.ensure_one()
        attendance_ids = self.env["resource.calendar.attendance"].search(
            [
                ("calendar_id", "=", self.resource_calendar_id.id),
                (
                    "dayofweek",
                    "=",
                    self.period_start.astimezone(timezone(self.env.user.tz)).weekday(),
                ),
            ]
        )
        service_ids = self.env["ni.service"].search(
            [
                ("attendance_ids", "in", attendance_ids.ids),
                "|",
                ("date", "=", False),
                ("date", "=", fields.Date.today()),
            ]
        )
        date_start = datetime.combine(date.today(), datetime.min.time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        date_end = datetime.combine(date.today(), datetime.max.time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        event_ids = self.env["ni.service.event"].search(
            [
                ("attendance_id", "in", attendance_ids.ids),
                ("start", ">=", date_start),
                ("start", "<=", date_end),
            ]
        )
        pprint.pprint(event_ids)
        attendance_service_map = {}
        for attendance in attendance_ids:
            event = event_ids.filtered_domain([("attendance_id", "=", attendance.id)])
            if event:
                attendance_service_map.update(
                    {
                        attendance.id: {
                            "service_id": event[0].service_id.id,
                            "service_event_id": event[0].id,
                        }
                    }
                )
                continue
            service = service_ids.filtered_domain(
                [("attendance_ids", "=", attendance.id)]
            )
            if service:
                attendance_service_map.update(
                    {attendance.id: {"service_id": service[0].id}}
                )
        self.service_attendance_ids = [fields.Command.clear()]
        self.service_attendance_ids = [
            fields.Command.create(
                {
                    "encounter_id": self.id,
                    "attendance_id": attendance_id,
                    "service_id": dict.get("service_id"),
                    "service_event_id": dict.get("service_event_id") or None,
                    "editable": service_ids.browse(dict.get("service_id")).editable,
                }
            )
            for attendance_id, dict in attendance_service_map.items()
        ]
