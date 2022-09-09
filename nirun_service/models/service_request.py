#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.nirun_patient.models.patient_res import create_patient_encounter_idx


class ServiceRequest(models.Model):
    _name = "ni.service.request"
    _description = "Service Request"
    _inherit = ["ni.patient.res", "period.mixin", "mail.thread", "ir.sequence.mixin"]
    _order = "id DESC"

    _check_period_start = True
    patient_id = fields.Many2one(readonly=True, states={"draft": [("readonly", False)]})
    encounter_id = fields.Many2one(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    name = fields.Char(default="New", readonly=True)
    display_name = fields.Char(compute="_compute_display_name")
    is_procedure = fields.Boolean()
    procedure_code_id = fields.Many2one(
        "ni.procedure.code", "Code", help="What is being requested/ordered"
    )
    procedure_category_id = fields.Many2one("ni.procedure.category", "Category")
    procedure_outcome_id = fields.Many2one("ni.procedure.outcome", "Outcome")
    procedure_ids = fields.One2many("ni.procedure", "service_request_id")
    procedure_count = fields.Integer(
        "Performed Count", compute="_compute_procedure", store=True
    )
    procedure_performed = fields.Datetime(
        "Last Performed",
        compute="_compute_procedure",
        store=True,
        help="Last procedure performed",
    )
    service_id = fields.Many2one(
        "ni.service",
        ondelete="restrict",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Requested performer",
    )
    service_available_type = fields.Selection(related="service_id.available_type")
    service_available_timing_ids = fields.One2many(
        related="service_id.available_timing_ids",
    )
    service_timing_id = fields.Many2one(
        "ni.service.timing",
        string="Event",
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="[('id', 'in', service_available_timing_ids)]",
        help="When service should occur",
    )
    service_available_time_ids = fields.One2many(
        related="service_id.available_time_ids"
    )
    service_time_id = fields.Many2one(
        "ni.service.time",
        string="Routine",
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="[('id', 'in', service_available_time_ids)]",
        help="What routine this request will participant",
    )
    display_time = fields.Char("Occurrence", compute="_compute_display_time")

    category_ids = fields.Many2many(related="service_id.category_ids")
    priority = fields.Selection(
        [("0", "Routine"), ("1", "Urgent"), ("2", "ASAP"), ("3", "STAT")],
        default="0",
        required=True,
        tracking=True,
    )
    intent = fields.Selection(
        [
            ("order", "Order"),
            ("plan", "Plan"),
            ("proposal", "Proposal"),
            ("option", "Option"),
        ],
        default="order",
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Request"),
            ("active", "In-Progress"),
            ("on-hold", "On-hold"),
            ("revoked", "Revoked"),
            ("completed", "Completed"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    requester_id = fields.Many2one(
        "res.partner",
        "Requester",
        default=lambda self: self.env.user.partner_id,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    instruction = fields.Text(help="Patient oriented instructions")
    approve_uid = fields.Many2one("res.users", "Approved by", readonly=True)
    approve_date = fields.Datetime("Approved on", readonly=True)

    def init(self):
        create_patient_encounter_idx(self)

    @api.depends("service_id", "patient_id", "state")
    def _compute_display_name(self):
        diff = dict(show_patient=None, show_state=None)
        names = dict(self.with_context(**diff).name_get())
        for rec in self:
            rec.display_name = names.get(rec.id)

    @api.depends("procedure_ids")
    def _compute_procedure(self):
        procedures = self.env["ni.procedure"].sudo()
        read = procedures.read_group(
            [("service_request_id", "in", self.ids)],
            ["service_request_id", "performed:max"],
            ["service_request_id"],
        )
        data = {
            res["service_request_id"][0]: {
                "performed": res["performed"],
                "count": res["service_request_id_count"],
            }
            for res in read
        }
        for rec in self:
            proc = data.get(rec.id, False)
            if proc:
                rec.procedure_count = proc.get("count", 0)
                rec.procedure_performed = proc.get("performed", False)

    def name_get(self):
        res = []
        for rec in self:
            name = rec._get_name()
            res.append((rec.id, name))
        return res

    def _get_name(self):
        self.ensure_one()
        rec = self
        name = "{}: {}".format(rec.name, rec.service_id.name)
        if self._context.get("show_id"):
            name = "#{}-{}".format(rec.id, name)
        if self._context.get("show_timing") and rec.timing_id:
            name = "{} ({})".format(name, rec.timing_id.name)
        if self._context.get("show_state"):
            name = "{} [{}]".format(name, rec._get_state_label())
        if self._context.get("show_patient"):
            name = "{}\n{}".format(name, rec.patient_id.name)
        return name

    @api.depends("service_time_id", "service_timing_id")
    def _compute_display_time(self):
        for rec in self:
            rec.display_time = rec.service_time_id.name or rec.service_timing_id.name

    def _get_state_label(self):
        self.ensure_one()
        return dict(self._fields["state"].selection).get(self.state)

    @api.onchange("service_id")
    def onchange_service_id(self):
        for rec in self:
            if rec.service_id:
                serv = rec.service_id
                rec.update(
                    {
                        "is_procedure": serv.is_procedure,
                        "procedure_code_id": serv.procedure_code_id.id,
                        "procedure_category_id": serv.procedure_category_id.id,
                        "procedure_outcome_id": serv.procedure_outcome_id.id,
                    }
                )

    @api.model
    def create(self, vals):
        res = super(ServiceRequest, self).create(vals)
        res.onchange_service_id()
        return res

    def action_approve(self):
        records = self.filtered(lambda rec: rec.state == "draft")
        records.write(
            {
                "state": "active",
                "approve_date": fields.Datetime.now(),
                "approve_uid": self.env.uid,
            }
        )

    def action_pause(self):
        records = self.filtered(lambda rec: rec.state == "active")
        records.write({"state": "on-hold"})

    def action_resume(self):
        records = self.filtered(lambda rec: rec.state == "on-hold")
        records.write({"state": "active"})

    def action_complete(self):
        records = self.filtered(lambda rec: rec.state == "active")
        records.write({"state": "completed"})

        today = fields.Date.today()
        records = records.filtered(
            lambda rec: not rec.period_end or rec.period_end > today
        )
        records.write({"period_end": today})

    def action_revoke(self):
        records = self.filtered(lambda rec: rec.state == "active")
        records.write({"state": "revoked"})

        today = fields.Date.today()
        records = records.filtered(
            lambda rec: not rec.period_end or rec.period_end > today
        )
        records.write({"period_end": today})

    @api.constrains("service_available_type", "service_time_id", "service_timing_id")
    def _check_service_time_or_timing(self):
        for rec in self:
            if rec.service_available_type == "event":
                if rec.service_time_id:
                    raise ValidationError(_("Must not have routine"))
                if rec.service_available_timing_ids and not rec.service_timing_id:
                    raise ValidationError(_("Must choose event"))
            else:  # type == 'routine
                if rec.service_timing_id:
                    raise ValidationError(_("Must not have event"))
                if rec.service_available_time_ids and not rec.service_time_id:
                    raise ValidationError(_("Must choose routine"))

    def create_procedure(self):
        no_active = self.filtered_domain([("state", "!=", "active")])
        if no_active:
            raise ValidationError(
                _("To create procedure, Request must be in active state")
            )

        procedures = self.env["ni.procedure"]
        for rec in self:
            procedures.create(
                {
                    "patient_id": rec.patient_id.id,
                    "encounter_id": rec.encounter_id.id,
                    "performed": fields.datetime.now(),
                    "service_request_id": rec.id,
                    "code_id": rec.procedure_code_id.id,
                    "state": "completed",
                    "outcome_id": rec.procedure_outcome_id.id
                    or self.ref("nirun_procedure.outcome_success"),
                }
            )
