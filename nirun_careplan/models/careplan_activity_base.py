#  Copyright (c) 2022-2023. NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Activity(models.AbstractModel):
    _name = "ni.careplan.activity.base"
    _description = "Careplan Activity"
    _order = "sequence"

    sequence = fields.Integer(help="Determine the display order", index=True)
    color = fields.Integer(string="Color Index")

    careplan_id = fields.Many2one(
        "ni.careplan",
        string="Care Plan",
        required=True,
        check_company=True,
        ondelete="cascade",
        copy=False,
        default=lambda self: self.env.context.get("default_careplan_id"),
    )
    careplan_state = fields.Selection(related="careplan_id.state")
    patient_id = fields.Many2one(related="careplan_id.patient_id")
    encounter_id = fields.Many2one(related="careplan_id.encounter_id")
    company_id = fields.Many2one(
        related="careplan_id.company_id", store=True, readonly=True, index=True
    )
    code_id = fields.Many2one(
        "ni.careplan.activity.code",
        "Activity",
        required=False,
        tracking=True,
        index=True,
        ondelete="restrict",
    )
    name = fields.Char(string="Activity", related="code_id.name")
    display_name = fields.Char(compute="_compute_display_name")
    description = fields.Html(string="Description")
    category_id = fields.Many2one("ni.careplan.category", tracking=True)
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Important")],
        default="0",
        index=True,
        string="Priority",
    )
    state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("in-progress", "In-Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="scheduled",
        tracking=True,
        copy=False,
        group_expand="_group_expand_state",
    )
    kind = fields.Selection(
        [
            ("ni.careplan.activity.code", "Activity"),
            ("ni.service.request", "Service"),
            # ("ni.medication.request", "Medication Request"),
        ],
        default="ni.careplan.activity.code",
    )
    service_id = fields.Many2one("ni.service")
    service_available_type = fields.Selection(related="service_id.available_type")
    service_available_timing_ids = fields.One2many(
        related="service_id.available_timing_ids",
    )
    service_available_time_ids = fields.One2many(
        related="service_id.available_time_ids"
    )
    service_request_id = fields.Many2one(
        "ni.service.request",
        domain="[('service_id', '=?', service_id), "
        "('patient_id', '=?', patient_id), "
        "('encounter_id', '=?', encounter_id)]",
    )
    service_timing_id = fields.Many2one(
        related="service_request_id.service_timing_id", readonly=False
    )
    service_time_id = fields.Many2one(
        related="service_request_id.service_time_id", readonly=False
    )

    _sql_constraints = [
        (
            "code__uniq",
            "unique (careplan_id, code_id)",
            "Activity must be unqiue!",
        ),
    ]

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        act = self
        name = act.code_id.name or act.service_id.name
        if self._context.get("show_patient"):
            name = "{} - {}".format(act.patient_id._name_get(), name)
        if self._context.get("show_state"):
            name = "{} ({})".format(name, act.get_state_label())
        return name

    def get_state_label(self):
        self.ensure_one()
        return dict(self._fields["state"].selection).get(self.state)

    @api.model
    def _group_expand_state(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.onchange("code_id", "service_id")
    def _onchange_code_id(self):
        for rec in self:
            if rec.kind == "ni.careplan.activity.code" and rec.code_id:
                rec.name = rec.code_id.name
            if rec.kind == "ni.service.request" and rec.service_request_id:
                rec.name = rec.service_request_id.service_id.name

    @api.onchange("category_id")
    def _onchange_category_id(self):
        for rec in self:
            if rec.category_id and not rec.color:
                rec.color = rec.category_id.color

    @api.depends("name")
    def _compute_display_name(self):
        diff = dict(show_patient=None, show_state=None)
        names = dict(self.with_context(**diff).name_get())
        for rec in self:
            rec.display_name = names.get(rec.id)

    def action_start(self, force=False):
        if not force:
            for act in self:
                if act.state != "scheduled":
                    raise ValidationError(_("Must be scheduled state"))
        self.write({"state": "in-progress"})

    def action_complete(self):
        for act in self:
            if act.state == "cancelled":
                raise ValidationError(_("Must be not be cancelled"))
        self.write({"state": "completed"})

    def action_cancel(self):
        for act in self:
            if act.state == "completed":
                raise ValidationError(_("Must be not be completed"))
        self.write({"state": "cancelled"})

    @api.constrains("code_id", "service_request_id")
    def check_code_or_ref(self):
        for rec in self:
            if not rec.code_id and not rec.service_request_id:
                raise ValidationError(
                    _("Must select activity or service/medication request")
                )
