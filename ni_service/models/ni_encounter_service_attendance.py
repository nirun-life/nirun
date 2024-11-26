#  Copyright (c) 2024 NSTDA

from pytz import timezone

from odoo import api, fields, models


class EncounterServiceAttendance(models.Model):
    _name = "ni.encounter.service.attendance"
    _description = "Service Attendance"
    _order = "sequence"

    sequence = fields.Integer(related="attendance_id.sequence", store=True)
    encounter_id = fields.Many2one("ni.encounter", required=True, ondelete="cascade")
    patient_id = fields.Many2one(
        related="encounter_id.patient_id", store=True, index=True
    )
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

    name = fields.Char(compute="_compute_name", store=True)

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
        domain="[('attendance_ids', '=', attendance_id)]",
        check_company=True,
        ondelete="restrict",
    )
    service_ids = fields.Many2many(
        "ni.service",
        "ni_encounter_service_attendance_rel",
        "attendance_id",
        "service_id",
        domain="[('attendance_ids', '=', attendance_id)]",
        check_company=True,
        ondelete="restrict",
    )
    service_event_id = fields.Many2one(
        "ni.service.event", index=True, domain="[('service_id', '=', service_id)]"
    )
    partner_ids = fields.Many2many(related="service_event_id.partner_ids")
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

    @api.depends("service_id", "service_ids")
    def _compute_name(self):
        for rec in self:
            if len(rec.service_ids) > 1:
                rec.name = ", ".join(rec.service_ids.mapped("name"))
            else:
                rec.name = rec.service_id.name
