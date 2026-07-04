#  Copyright (c) 2024 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Service(models.Model):
    _name = "ni.service"
    _description = "Service"
    _inherit = "ni.coding"
    _order = "sequence"

    _rec_name = "name"

    @api.model
    def default_get(self, fields):
        res = super(Service, self).default_get(fields)
        if "company_id" in res:
            comp = self.env["res.company"].browse(res["company_id"])
            if comp.service_calendar_id:
                res["calendar_id"] = self.env["resource.calendar"].browse(
                    comp.service_calendar_id.id
                )
        return res

    sequence = fields.Integer()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    company_multi_category = fields.Boolean(related="company_id.service_multi_category")
    name = fields.Char("Service", required=True)
    description = fields.Html()
    category_id = fields.Many2one("ni.service.category", index=True)
    category_ids = fields.Many2many(
        "ni.service.category",
        "ni_service_category_rel",
        "service_id",
        "category_id",
        string="Categories",
    )
    category = fields.Char(compute="_compute_category", store=True)
    category_decoration = fields.Selection(related="category_id.decoration")
    type_id = fields.Many2one("ni.service.type", index=True)
    type_decoration = fields.Selection(related="type_id.decoration")
    calendar_id = fields.Many2one(
        "resource.calendar", required=False, domain="[('company_id', '=', company_id)]"
    )
    calendar_ids = fields.Many2many(
        "resource.calendar", compute="_compute_calendar_ids"
    )
    calendar_count = fields.Integer(compute="_compute_calendar_ids")
    duration = fields.Float()
    attendance_ids = fields.Many2many(
        "resource.calendar.attendance",
        "ni_service_event_attendance_rel",
        "service_id",
        "attendance_id",
        domain="[('calendar_id', '=', calendar_id)]",
        index=True,
    )
    attendance_count = fields.Integer(compute="_compute_attendance_count")
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
        required=True,
        index=True,
        default="0",
    )
    next_date = fields.Date(compute="_compute_date")
    encounter_ids = fields.Many2many(
        "ni.encounter", domain="[('company_id', '=', company_id)]"
    )
    specialty_ids = fields.Many2many(
        "hr.job", "ni_service_specialty", "service_id", "job_id"
    )
    patient_ids = fields.Many2many("ni.patient", compute="_compute_patient")
    employee_ids = fields.Many2many(
        "hr.employee",
        string="Participant",
        domain="[('company_id', '=', company_id)]",
        check_company=True,
    )
    employee_id = fields.Many2one("hr.employee", "Responsible", check_company=True)
    employee_count = fields.Integer(
        "Participant Count", compute="_compute_employee_count"
    )
    recurrence = fields.Boolean(default=True)
    calendar = fields.Boolean(
        default=False, help="Indicate this service will be booking in to calendar"
    )
    editable = fields.Boolean(
        default=True, help="Indicate user can edit this service or not when generate"
    )
    event_ids = fields.One2many("ni.service.event", "service_id")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "system_name_uniq",
            "unique (company_id, name, type_id)",
            "This name already exists!",
        )
    ]

    @api.depends("category_id", "category_ids")
    def _compute_category(self):
        for rec in self:
            categories = rec.category_ids or rec.category_id
            rec.category = ", ".join(categories.mapped("name")) if categories else False

    def _sync_category_relations(self):
        for rec in self:
            if rec.category_ids and not rec.category_id:
                rec.with_context(skip_category_sync=True).write(
                    {"category_id": rec.category_ids[0].id}
                )
            elif rec.category_id and not rec.category_ids:
                rec.with_context(skip_category_sync=True).write(
                    {"category_ids": [fields.Command.set([rec.category_id.id])]}
                )
            elif rec.category_id and rec.category_id not in rec.category_ids:
                rec.with_context(skip_category_sync=True).write(
                    {"category_ids": [fields.Command.link(rec.category_id.id)]}
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get("skip_category_sync"):
            records._sync_category_relations()
        return records

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("skip_category_sync"):
            self._sync_category_relations()
        return res

    @api.constrains("company_id", "category_ids")
    def _check_category_mode(self):
        for rec in self:
            if rec.company_id.service_multi_category:
                continue
            if len(rec.category_ids) > 1:
                raise ValidationError(
                    _("Multiple service categories are not allowed for this company.")
                )

    def get_default_calendar(self, raise_err=False):
        self.ensure_one()
        if self.calendar_id:
            return self.calendar_id
        elif self.calendar_ids:
            return self.calendar_ids[0]
        elif raise_err:
            raise ValidationError(
                _("Misconfiguration on {}, please contact the administrator").format(
                    self.name
                )
            )
        else:
            return None

    @api.depends("attendance_ids")
    def _compute_calendar_ids(self):
        for rec in self:
            if rec.attendance_ids:
                calendar = rec.attendance_ids.mapped("calendar_id")
                rec.update(
                    {
                        "calendar_ids": [fields.Command.set(calendar.ids)],
                        "calendar_count": len(calendar),
                    }
                )
            else:
                rec.update(
                    {"calendar_ids": [fields.Command.clear()], "calendar_count": 0}
                )

    def action_default_attendance(self):
        for rec in self:
            if (
                rec.calendar_id == rec.company_id.service_calendar_id
                and rec.company_id.service_attendance_ids
            ):
                rec.attendance_ids = rec.company_id.service_attendance_ids
            else:
                rec.attendance_ids = rec.calendar_id.attendance_ids

    @api.depends("event_ids")
    def _compute_date(self):
        now = fields.Datetime.now()
        today = now.replace(hour=0, minute=0, second=0)
        events = (
            self.env["ni.service.event"]
            .sudo()
            .search(
                [("service_id", "in", self.ids), ("start", ">", today)],
                order="service_id, start",
            )
        )
        next_start = {}
        for event in events:
            next_start.setdefault(event.service_id.id, event.start)
        for rec in self:
            start = next_start.get(rec.id)
            rec.next_date = start.date() if start else None

    @api.onchange("attendance_ids")
    def _onchange_attendance_ids(self):
        for rec in self:
            if rec.attendance_ids:
                att = rec.attendance_ids[0]
                rec.duration = att.hour_to - att.hour_from

    @api.constrains("attendance_ids", "duration")
    def _check_duration(self):
        for rec in self:
            if rec.attendance_ids and not rec.duration:
                rec._onchange_attendance_ids()

    @api.depends("attendance_ids")
    def _compute_attendance_count(self):
        for rec in self:
            rec.attendance_count = len(rec.attendance_ids)

    @api.depends("encounter_ids")
    def _compute_patient(self):
        for rec in self:
            rec.patient_ids = rec.encounter_ids.mapped("patient_id")

    @api.constrains("employee_id", "employee_ids")
    def _check_employee_id(self):
        for rec in self:
            if rec.employee_id and rec.employee_id not in rec.employee_ids:
                rec.employee_ids = [fields.Command.link(rec.employee_id.id)]

    @api.depends("employee_ids")
    def _compute_employee_count(self):
        for rec in self:
            rec.employee_count = len(rec.employee_ids)

    def create_event(self):
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_name": self.name,
                "default_service_id": self.id,
                "default_res_model": self._name,
                "default_res_id": self.id,
                "default_mode": "multi",
            }
        )
        view = {
            "name": "Calendar",
            "res_model": "ni.service.event",
            "type": "ir.actions.act_window",
            "target": self.env.context.get("target", "current"),
            "view_mode": "calendar,tree,form",
            "domain": [("service_ids", "=", self.id)],
            "context": ctx,
        }
        return view

    @api.model
    def _cron_backfill_category_ids(self):
        self.search([("category_id", "!=", False)])._sync_category_relations()
        cron = self.env.ref(
            "ni_service.ir_cron_backfill_category_ids", raise_if_not_found=False
        )
        if cron:
            cron.sudo().write({"active": False})
