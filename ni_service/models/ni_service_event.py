#  Copyright (c) 2024 NSTDA
from datetime import datetime, timedelta

from pytz import timezone

from odoo import api, fields, models
from odoo.tools import pytz


class ServiceEvent(models.Model):
    _name = "ni.service.event"
    _description = "Service Calendar"
    _inherit = "mail.thread"
    _inherits = {"calendar.event": "event_id"}
    _rec_name = "service_id"

    event_id = fields.Many2one("calendar.event", required=True, ondelete="cascade")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    service_id = fields.Many2one(
        "ni.service",
        required=True,
        ondelete="restrict",
        check_company=True,
        domain=lambda self: [
            ("category_id", "!=", self.env.ref("ni_service.categ_routine").id),
        ],
    )

    attendance_id = fields.Many2one(
        "resource.calendar.attendance",
        required=True,
        domain="[('id', 'in', service_attendance_id), ('dayofweek', '=?', dayofweek)]",
    )
    service_attendance_id = fields.Many2many(
        related="service_id.attendance_ids", help="Use to filter attendance_id"
    )
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
        help="Use to filter attendance_id",
    )

    encounter_service_attendance_ids = fields.One2many(
        "ni.encounter.service.attendance",
        "service_event_id",
        help="Encounter relate to this event",
    )
    encounter_ids = fields.Many2many("ni.encounter", compute="_compute_encounter")
    encounter_count = fields.Integer(compute="_compute_encounter")
    patient_ids = fields.Many2many("ni.patient", compute="_compute_encounter")
    patient_count = fields.Integer(compute="_compute_encounter")

    message_follower_ids = fields.One2many(related="event_id.message_follower_ids")
    message_ids = fields.One2many(related="event_id.message_ids")

    plan_patient_ids = fields.Many2many(
        "ni.patient",
        string="ผู้รับบริการ (วางแผน)",
        check_company=True,
        domain="[('presence_state', '!=', 'deceased')]",
    )
    plan_patient_count = fields.Integer(compute="_compute_plan_patient")
    display_plan_patient = fields.Boolean(compute="_compute_plan_patient")

    @api.depends("plan_patient_ids", "stop")
    def _compute_plan_patient(self):
        for rec in self:
            rec.plan_patient_count = len(rec.plan_patient_ids)
            if not rec.plan_patient_count:
                rec.display_plan_patient = False
            else:
                now = fields.Datetime.now()
                rec.display_plan_patient = now < rec.stop

    @api.depends("encounter_service_attendance_ids")
    def _compute_encounter(self):
        for rec in self:
            rec.encounter_ids = rec.encounter_service_attendance_ids.mapped(
                "encounter_id"
            )
            rec.encounter_count = len(rec.encounter_ids)
            rec.patient_ids = rec.encounter_ids.mapped("patient_id")
            rec.patient_count = len(rec.patient_ids)

    @api.onchange("service_id")
    def _onchange_service_id(self):
        for rec in self:
            if not rec.service_id:
                continue
            rec.name = rec.service_id.name
            rec.partner_ids = rec.service_id.employee_ids.mapped(
                lambda r: r.user_partner_id | r.work_contact_id
            )
            if rec.service_id.employee_id and rec.service_id.employee_id.user_id:
                rec.user_id = rec.service_id.employee_id.user_id
            else:
                rec.user_id = self.env.user

    @api.onchange("attendance_id")
    @api.constrains("attendance_id", "start_date")
    def _onchange_attendance_id(self):
        for rec in self:
            if not rec.attendance_id:
                continue
            date = rec.start_date or rec.start.date() or fields.Date.today()
            tz = rec.event_tz or self.env.user.tz
            rec.start = self.float_time_to_datetime(
                date, rec.attendance_id.hour_from, tz
            )
            rec.stop = self.float_time_to_datetime(date, rec.attendance_id.hour_to, tz)
            rec.allday = False

    def float_time_to_datetime(self, date, float_time, tz=None):
        if not float_time:
            return False
        if not date:
            date = fields.Date.today()
        if not tz:
            tz = self.env.user.tz

        start_of_day = datetime.now(timezone(tz)).replace(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        hours = int(float_time)
        minutes = int((float_time - hours) * 60)

        local_dt = start_of_day + timedelta(hours=hours, minutes=minutes)
        return local_dt.astimezone(pytz.UTC).replace(tzinfo=None)

    @api.depends("start_date")
    def _compute_dayofweek(self):
        for rec in self:
            date = rec.start_date or rec.start
            rec.dayofweek = str(date.weekday()) if date else None

    def action_open_calendar_event(self):
        return self.event_id.action_open_calendar_event()

    def action_open_composer(self):
        return self.event_id.action_open_composer()

    def action_join_video_call(self):
        return self.event_id.action_join_video_call()

    def clear_videocall_location(self):
        return self.event_id.clear_videocall_location()

    def set_discuss_videocall_location(self):
        return self.event_id.set_discuss_videocall_location()

    def action_sendmail(self):
        return self.event_id.action_sendmail()
