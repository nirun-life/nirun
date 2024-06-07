#  Copyright (c) 2024 NSTDA

from pytz import timezone

from odoo import api, fields, models


class EncounterServiceAttendance(models.Model):
    _name = "ni.encounter.service.attendance"
    _description = "Service Attendance"
    _order = "sequence"

    sequence = fields.Integer(related="attendance_id.sequence", store=True)
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
    service_event_id = fields.Many2one(
        "ni.service.event", domain="[('service_id', '=', service_id)]"
    )
    calendar_event_id = fields.Many2one(related="service_event_id.event_id")
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
