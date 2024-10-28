#  Copyright (c) 2024 NSTDA
from datetime import datetime, timedelta

from pytz import timezone

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import pytz


class Event(models.Model):
    _inherit = "calendar.event"

    @api.model
    def _get_public_fields(self):
        # Work around to prevent maximum recursive errors when open event from other user who not service event's creator
        return super(Event, self)._get_public_fields() | {"attendee_ids"}


class ServiceEvent(models.Model):
    _name = "ni.service.event"
    _description = "Service Calendar"
    _inherit = "mail.thread"
    _inherits = {"calendar.event": "event_id"}
    _order = "start desc, id desc"

    @api.model
    def default_get(self, fields):
        res = super(ServiceEvent, self).default_get(fields)
        if "service_ids" in fields and "service_ids" not in res:
            if self.env.context.get("default_service_id"):
                res["service_ids"] = [
                    Command.link(self.env.context["default_service_id"])
                ]
        return res

    user_specialty = fields.Many2one(
        "hr.job", default=lambda self: self.env.user.employee_id.job_id, store=False
    )

    event_id = fields.Many2one("calendar.event", required=True, ondelete="cascade")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    mode = fields.Selection(
        [("single", "Single Service"), ("multi", "Multi-Services")],
        default="multi",
        required=True,
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
    service_ids = fields.Many2many(
        "ni.service",
        "ni_service_event_rel",
        "event_id",
        "service_id",
        domain=lambda self: [
            ("category_id", "!=", self.env.ref("ni_service.categ_routine").id),
        ],
    )
    service_count = fields.Integer(compute="_compute_service_count")
    user_id = fields.Many2one(
        related="event_id.user_id", string="ผู้รับผิดชอบหลัก", readonly=False
    )
    service_type_id = fields.Many2one(related="service_id.type_id")
    service_category_ids = fields.Many2many(
        "ni.service.category", compute="_compute_service_category_ids", store=True
    )
    service_category_id = fields.Many2one("ni.service.category")

    attendance_id = fields.Many2one(
        "resource.calendar.attendance",
        required=False,
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
    color = fields.Integer()

    image_1 = fields.Image()
    image_2 = fields.Image()
    has_image = fields.Boolean(compute="_compute_attachment")
    attachment_ids = fields.Many2many("ir.attachment", compute="_compute_attachment")

    @api.depends("image_1", "image_2")
    def _compute_attachment(self):
        for rec in self:
            rec.attachment_ids = self.env["ir.attachment"].search(
                [("res_model", "=", self._name), ("res_id", "=", rec.id)]
            )
            rec.has_image = any([rec.image_1, rec.image_2])

    @api.depends("service_ids")
    def _compute_service_category_ids(self):
        for rec in self:
            rec.service_category_ids = (
                [fields.Command.set(rec.service_ids.mapped("category_id").ids)]
                if rec.service_ids
                else [fields.Command.set(rec.service_id.mapped("category_id").ids)]
            )

    @api.constrains("service_category_id", "service_id", "color")
    def _check_color(self):
        for rec in self:
            if not rec.service_category_id and rec.service_category_ids:
                rec.service_category_id = rec.service_category_ids[0]
            if rec.service_category_id and rec.color != rec.service_category_id.color:
                rec.color = rec.service_category_id.color

    @api.depends("service_id", "service_ids")
    def _compute_service_count(self):
        for rec in self:
            rec.service_count = (
                len(rec.service_ids) if rec.service_ids else 1 if rec.service_id else 0
            )

    @api.onchange("service_ids", "mode")
    def _onchange_service_ids(self):
        for rec in self:
            if rec.service_ids:
                if not rec.service_id or rec.service_id not in rec.service_ids.mapped(
                    "id"
                ):
                    rec.service_id = rec.service_ids[0]

    @api.depends("plan_patient_ids", "stop")
    def _compute_plan_patient(self):
        for rec in self:
            rec.plan_patient_count = len(rec.plan_patient_ids)
            if not rec.plan_patient_count:
                rec.display_plan_patient = False
            else:
                today = fields.Date.today()
                rec.display_plan_patient = (
                    today <= rec.stop.date()
                    and not rec.encounter_service_attendance_ids
                )

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
            if len(rec.service_ids) <= 1:
                rec.service_ids = [Command.set([rec.service_id.id])]
            rec.name = rec.service_id.name
            rec.partner_ids = rec.service_id.employee_ids.mapped(
                lambda r: r.user_partner_id | r.work_contact_id
            )
            if rec.service_id.employee_id and rec.service_id.employee_id.user_id:
                rec.user_id = rec.service_id.employee_id.user_id
            else:
                rec.user_id = self.env.user

    @api.constrains("user_id", "partner_ids")
    def _check_user_partner(self):
        for rec in self:
            if not rec.user_id:
                continue
            if rec.user_id.partner_id and rec.user_id.partner_id not in rec.partner_ids:
                rec.partner_ids = [fields.Command.link(rec.user_id.partner_id.id)]

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

    @api.constrains("service_id", "service_ids", "mode")
    def _check_service_name(self):
        for rec in self:
            if (rec.mode == "single" and not rec.service_id) or (
                rec.mode == "multi" and not rec.service_ids
            ):
                raise UserError(_("Please select at least one service"))
            if rec.mode == "single" and rec.service_count > 1:
                rec.service_ids = [Command.set([rec.service_id.id])]
            if rec.mode == "multi":
                if not rec.service_id:
                    rec.service_id = rec.service_ids[0]
                if rec.service_count == 1:
                    rec.mode = "single"

            if rec.service_count > 1:
                rec.name = ", ".join(rec.service_ids.mapped("name"))
            else:
                rec.name = rec.service_id.name
