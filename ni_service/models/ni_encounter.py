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
    service_resource_ids = fields.One2many(
        "ni.encounter.service.resource", "encounter_id"
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
                attendance_service_map.update({attendance.id: event[0].service_id.id})
                continue
            service = service_ids.filtered_domain(
                [("attendance_ids", "=", attendance.id)]
            )
            if service:
                attendance_service_map.update({attendance.id: service[0].id})

        self.service_resource_ids = [
            fields.Command.create(
                {
                    "encounter_id": self.id,
                    "attendance_id": attendance_id,
                    "service_id": service_id,
                    "editable": service_ids.browse(service_id).editable,
                }
            )
            for attendance_id, service_id in attendance_service_map.items()
        ]


class EncounterServiceResource(models.Model):
    _name = "ni.encounter.service.resource"
    _description = "Service Resource"
    _order = "sequence"

    sequence = fields.Integer(related="attendance_id.sequence")
    encounter_id = fields.Many2one("ni.encounter", required=True, ondelete="cascade")
    encounter_date = fields.Datetime(related="encounter_id.period_start", string="Date")
    dayofweek = fields.Selection(
        [
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        "Day of Week",
        compute="_compute_dayofweek",
    )
    resource_calendar_id = fields.Many2one(related="encounter_id.resource_calendar_id")

    attendance_id = fields.Many2one(
        "resource.calendar.attendance",
        "เวลา",
        required=True,
        domain="[('calendar_id','=?', resource_calendar_id)]",
    )
    service_id = fields.Many2one(
        "ni.service",
        "กิจกรรม",
        required=True,
        domain="[('attendance_ids', '=', attendance_id), '|', ('date', '=', False), ('date', '=', encounter_date)]",
        check_company=True,
    )
    employee_id = fields.Many2one(related="service_id.employee_id")
    employee_ids = fields.Many2many(related="service_id.employee_ids")
    editable = fields.Boolean(default=True)
    note = fields.Text()

    _sql_constraints = [
        (
            "encounter_attendance_uniq",
            "unique (encounter_id, attendance_id)",
            "The attendance time must be unique!",
        ),
    ]

    @api.depends("encounter_id", "encounter_date")
    def _compute_dayofweek(self):
        for rec in self:
            rec.dayofweek = str(
                rec.encounter_date.astimezone(timezone(self.env.user.tz)).weekday()
            )
