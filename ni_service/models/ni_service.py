#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class Service(models.Model):
    _name = "ni.service"
    _description = "Service"
    _inherit = "ni.coding"

    sequence = fields.Integer()

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

    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    name = fields.Char("Service", required=True)
    description = fields.Html()
    category_id = fields.Many2one("ni.service.category")
    type_id = fields.Many2one("ni.service.type")
    calendar_id = fields.Many2one(
        "resource.calendar", required=True, domain="[('company_id', '=', company_id)]"
    )
    duration = fields.Float()
    attendance_ids = fields.Many2many(
        "resource.calendar.attendance",
        "ni_service_event_attendance_rel",
        "service_id",
        "attendance_id",
        domain="[('calendar_id', '=', calendar_id)]",
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

    date = fields.Date()
    encounter_ids = fields.Many2many(
        "ni.encounter", domain="[('company_id', '=', company_id)]"
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
                "default_start_date": fields.Date.today(),
                "default_res_model": self._name,
                "default_res_id": self.id,
            }
        )
        view = {
            "name": "Event",
            "res_model": "ni.service.event",
            "type": "ir.actions.act_window",
            "target": self.env.context.get("target", "current"),
            "view_mode": "calendar,tree,form",
            "domain": [("service_id", "=", self.id)],
            "context": ctx,
        }
        return view
