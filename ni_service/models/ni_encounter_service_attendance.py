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
    resource_calendar_id = fields.Many2one(
        related="encounter_id.resource_calendar_id", store=True
    )

    name = fields.Char(compute="_compute_name", store=True)

    attendance_id = fields.Many2one(
        "resource.calendar.attendance",
        "เวลา",
        required=True,
        domain="[('calendar_id','=?', resource_calendar_id)]",
    )
    hour_from = fields.Float(related="attendance_id.hour_from", store=True)
    hour_to = fields.Float(related="attendance_id.hour_to", store=True)
    category_id = fields.Many2one(
        related="service_id.category_id",
        store=True,
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
    request_id = fields.Many2one(
        "ni.service.request",
        "Based On Request",
        ondelete="set null",
        index=True,
        help="Request of this attendance",
    )
    service_event_id = fields.Many2one(
        "ni.service.event", index=True, domain="[('service_id', '=', service_id)]"
    )
    start = fields.Datetime(related="service_event_id.start", store=True)
    duration = fields.Float(related="service_event_id.duration", store=True)
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

    def _find_matching_request(self):
        self.ensure_one()
        if not self.patient_id:
            return None
        service_ids = self.service_ids.ids or (
            [self.service_id.id] if self.service_id else []
        )
        if not service_ids:
            return None
        encounter_date = self.encounter_date
        domain = [
            ("patient_id", "=", self.patient_id.id),
            ("service_ids", "in", service_ids),
        ]
        if encounter_date:
            domain += [
                "|",
                ("period_start", "=", False),
                ("period_start", "<=", encounter_date),
                "|",
                ("period_end", "=", False),
                ("period_end", ">=", encounter_date),
            ]
        return self.env["ni.service.request"].search(domain, limit=1)

    @api.onchange("service_id", "service_ids", "encounter_id")
    def _onchange_auto_request(self):
        for rec in self:
            if not rec.request_id:
                rec.request_id = rec._find_matching_request()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if not rec.request_id:
                rec.request_id = rec._find_matching_request()
        return records

    @api.depends("service_id", "service_ids")
    def _compute_name(self):
        for rec in self:
            if len(rec.service_ids) > 1:
                rec.name = ", ".join(rec.service_ids.mapped("name"))
            else:
                rec.name = rec.service_id.name
