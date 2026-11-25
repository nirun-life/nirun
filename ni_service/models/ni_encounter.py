#  Copyright (c) 2024 NSTDA
from datetime import datetime

from pytz import UTC

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    resource_calendar_id = fields.Many2one(
        "resource.calendar",
        "Calendar",
        check_company=True,
    )
    service_attendance_ids = fields.One2many(
        "ni.encounter.service.attendance",
        "encounter_id",
    )
    service_request_ids = fields.One2many("ni.service.request", "encounter_id")

    @api.onchange("class_id")
    def _onchange_class_id(self):
        for rec in self:
            if rec.class_id.service_calendar_id:
                rec.resource_calendar_id = rec.class_id.service_calendar_id

    def action_generate_service_resource(self):
        self.ensure_one()
        local_start = fields.Datetime.context_timestamp(self, self.period_start)
        attendance_ids = self.env["resource.calendar.attendance"].search(
            [
                ("calendar_id", "=", self.resource_calendar_id.id),
                ("dayofweek", "=", str(local_start.weekday())),
            ]
        )
        service_ids = self.env["ni.service"].search(
            [("attendance_ids", "in", attendance_ids.ids)]
        )
        # events of the day of the user, as for the day of week above
        date_start, date_end = (
            local_start.tzinfo.localize(datetime.combine(local_start.date(), time))
            .astimezone(UTC)
            .replace(tzinfo=None)
            for time in (datetime.min.time(), datetime.max.time())
        )
        event_ids = self.env["ni.service.event"].search(
            [
                ("attendance_ids", "in", attendance_ids.ids),
                ("start", ">=", date_start),
                ("start", "<=", date_end),
            ]
        )
        attendance_service_map = {}
        for attendance in attendance_ids:
            scheduled_event = event_ids.filtered_domain(
                [("attendance_ids", "=", attendance.id)]
            )
            planned_event = scheduled_event.filtered_domain(
                [("plan_patient_ids", "=", self.patient_id.id)]
            )
            e = None
            if planned_event:
                e = planned_event[0]
            elif scheduled_event:
                e = scheduled_event.sorted("plan_patient_count")[0]
            if e:
                attendance_service_map.update(
                    {
                        attendance.id: {
                            "name": e.name,
                            "service_id": e.service_id.id,
                            "service_ids": [
                                fields.Command.set(e.service_ids.mapped("id"))
                            ],
                            "service_event_id": e.id,
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
                    "name": dict.get("name"),
                    "encounter_id": self.id,
                    "attendance_id": attendance_id,
                    "service_id": dict.get("service_id"),
                    "service_ids": dict.get("service_ids"),
                    "service_event_id": dict.get("service_event_id") or None,
                    "editable": service_ids.browse(dict.get("service_id")).editable,
                }
            )
            for attendance_id, dict in attendance_service_map.items()
        ]
