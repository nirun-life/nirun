#  Copyright (c) 2024 NSTDA
from datetime import datetime, timedelta

from pytz import timezone

from odoo import SUPERUSER_ID, _, api, fields, models
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

    @api.model
    def _read_group_category_ids(self, category, domain, order):
        # We need this to show all service category on kanban view
        category_ids = category._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return category.browse(category_ids)

    user_specialty = fields.Many2one(
        "hr.job", default=lambda self: self.env.user.employee_id.job_id, store=False
    )
    start = fields.Datetime(
        related="event_id.start", inherited=True, store=True, readonly=False, index=True
    )
    stop = fields.Datetime(
        related="event_id.stop", inherited=True, store=True, readonly=False
    )
    duration = fields.Float(
        related="event_id.duration", inherited=True, store=True, readonly=False
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
        ondelete="restrict",
        check_company=True,
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
        "ni.service.category",
        string="Category Tags",
        compute="_compute_service_category_ids",
        store=True,
    )
    service_category_id = fields.Many2one(
        "ni.service.category",
        string="Category",
        group_expand="_read_group_category_ids",
    )
    calendar_id = fields.Many2one(
        "resource.calendar", domain="[('id', 'in', service_calendar_ids)]"
    )
    service_calendar_ids = fields.Many2many(
        related="service_id.calendar_ids", help="Use to filter calendar_id"
    )
    service_calendar_count = fields.Integer(related="service_id.calendar_count")

    attendance_id = fields.Many2one(
        "resource.calendar.attendance",
        required=False,
        domain="[('calendar_id', '=', calendar_id), ('dayofweek', '=?', dayofweek), ('id', 'in', service_attendance_id),  ]",
        compute="_compute_attendance_id",
        inverse="_inverse_attendance_id",
    )
    attendance_ids = fields.Many2many(
        "resource.calendar.attendance",
        domain="[('calendar_id', '=', calendar_id),  ('dayofweek', '=?', dayofweek), ('id', 'in', service_attendance_id),]",
    )
    service_attendance_id = fields.Many2many(
        related="service_id.attendance_ids", help="Use to filter attendance_id"
    )
    service_attendance_count = fields.Integer(related="service_id.attendance_count")
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
    has_image = fields.Boolean(compute="_compute_attachment_ids")
    attachment_ids = fields.One2many(
        "ir.attachment",
        compute="_compute_attachment_ids",
        string="Main Attachments",
        help="Attachments that don't come from a message.",
    )
    displayed_image_id = fields.Many2one(
        "ir.attachment",
        domain="[('res_model', '=', 'ni.service.event'),"
        "('res_id', '=', id), "
        "('mimetype', 'ilike', 'image')]",
        string="Cover Image",
    )

    def _get_attachments_search_domain(self):
        self.ensure_one()
        return [("res_id", "=", self.id), ("res_model", "=", "ni.service.event")]

    def _compute_attachment_ids(self):
        for task in self:
            attachment_ids = (
                self.env["ir.attachment"]
                .search(task._get_attachments_search_domain())
                .ids
            )
            message_attachment_ids = task.mapped(
                "message_ids.attachment_ids"
            ).ids  # from mail_thread
            task.attachment_ids = [
                (6, 0, list(set(attachment_ids) - set(message_attachment_ids)))
            ]
            task.has_image = bool(attachment_ids)

    @api.depends("attendance_ids")
    def _compute_attendance_id(self):
        for rec in self:
            rec.attendance_id = rec.attendance_ids[0] if rec.attendance_ids else None

    def _inverse_attendance_id(self):
        for rec in self:
            if rec.attendance_id and rec.attendance_id not in rec.attendance_ids:
                rec.attendance_ids = [(fields.Command.link(rec.attendance_id.id))]

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
            rec.calendar_id = rec.service_id.get_default_calendar()
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

    @api.onchange("attendance_ids", "attendance_id", "start")
    def _onchange_attendance_id(self):
        for rec in self:
            if rec.attendance_ids:
                remove_att = rec.attendance_ids.filtered(
                    lambda a: a.dayofweek != rec.dayofweek
                )
                if remove_att:
                    rec.attendance_ids = [
                        fields.Command.unlink(a.id) for a in remove_att
                    ]
            if not rec.attendance_id:
                continue

            date = rec.start_date or rec.start.date() or fields.Date.today()
            tz = rec.event_tz or self.env.user.tz
            attends = rec.attendance_ids.sorted("hour_from")
            rec.start = self.float_time_to_datetime(date, attends[0].hour_from, tz)
            rec.stop = self.float_time_to_datetime(date, attends[-1].hour_to, tz)
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

    @api.constrains("service_id", "calendar_id", "attendance_ids")
    def _check_calendar_attendance_rel(self):
        for rec in self:
            if not rec.service_id or not rec.service_attendance_id:
                continue
            if not rec.calendar_id or not rec.attendance_ids:
                raise UserError(_("Please specify calendar and attendance"))

            if rec.attendance_ids[0].calendar_id != rec.calendar_id:
                rec.attendance_ids = None

    @api.constrains("attendance_ids")
    def _check_sequence_attendance(self):
        for rec in self:
            if len(rec.attendance_ids) <= 1:
                continue
            attends = rec.attendance_ids.sorted("hour_from")
            end_hour = attends[0].hour_from
            for att in attends:
                diff = att.hour_from - end_hour
                if diff > 0.1668:
                    raise UserError(_("Attendance times must be sequential"))
                end_hour = att.hour_to
