#  Copyright (c) 2021-2023 NSTDA
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Condition(models.Model):
    _name = "ni.condition"
    _description = "Condition"
    _inherit = ["ni.period.mixin", "ni.patient.res"]
    _workflow_occurrence = "create_date"
    _check_period_start = False

    name = fields.Char("Condition Name", required=True)
    is_problem = fields.Boolean(
        "Chronic",
        compute="_compute_category",
        inverse="_inverse_is_problem",
        store=True,
        help="Save on Problem List Item",
    )
    is_diagnosis = fields.Boolean(
        "Diagnosis",
        compute="_compute_category",
        inverse="_inverse_is_diagnosis",
        store=True,
        help="Condition that relate to encounter",
    )
    code_id = fields.Many2one(
        "ni.condition.code",
        "Condition Code",
        required=False,
        ondelete="restrict",
        index=True,
        domain="[('system_id', '=', system_id)]",
    )

    def _get_default_system_id(self):
        system_ids = self.env.company.condition_system_ids
        return system_ids and system_ids[0].id or None

    system_id = fields.Many2one(
        "ni.coding.system",
        domain="[('id', 'in', system_ids)]",
        default=lambda self: self._get_default_system_id(),
    )
    system_ids = fields.Many2many(related="company_id.condition_system_ids")

    category_ids = fields.Many2many(
        "ni.condition.category",
        "ni_condition_category_rel",
        "condition_id",
        "category_id",
    )
    code = fields.Char(related="code_id.code", store=True)
    severity = fields.Selection(
        [("mild", "Mild"), ("moderate", "Moderate"), ("severe", "Severe")],
        required=False,
    )
    period_type = fields.Selection(
        [
            ("age", "Onset Age"),
            ("date", "Onset Date"),
            ("datetime", "Onset"),
        ],
        required=True,
        default="date",
    )
    period_start = fields.Datetime("Onset", default=None)
    period_start_date = fields.Date(
        "Onset Date",
        default=None,
        compute="_compute_period_start_date",
        inverse="_inverse_period_start_date",
    )
    period_end = fields.Datetime("Abatement")
    period_end_date = fields.Date(
        "Abatement Date",
        compute="_compute_period_end_date",
        inverse="_inverse_period_end_date",
    )
    age_start = fields.Integer(
        "Onset Age", compute="_compute_age", inverse="_inverse_age_start"
    )
    age_end = fields.Integer(
        "Abatement Age", compute="_compute_age", inverse="_inverse_age_end"
    )
    clinical_state = fields.Selection(
        [
            ("active", "Suffering"),
            ("recurrence", "Recurrence"),
            ("relapse", "Relapse"),
            ("inactive", "Inactive"),
            ("remission", "Remission"),
            ("resolved", "Resolved"),
        ],
        string="Status",
        copy=False,
        index=True,
        default="active",
    )
    verification_id = fields.Many2one("ni.condition.verification", "")
    note = fields.Text()
    diagnosis_ids = fields.One2many(
        "ni.encounter.diagnosis", "condition_id", readonly=True
    )

    observation_ids = fields.One2many(
        "ni.patient.observation", compute="_compute_observation"
    )
    observation_count = fields.Integer(compute="_compute_observation")

    _sql_constraints = [
        (
            "patient_id_code_id_uniq",
            "unique (patient_id, code_id)",
            "Patient already have this condition!",
        ),
    ]

    @api.depends("code_id", "patient_id")
    def _compute_observation(self):
        for rec in self:
            if rec.patient_id and rec.code_id and rec.code_id.observation_code_ids:
                observation = self.env["ni.patient.observation"].search(
                    [
                        ("patient_id", "=", rec.patient_id.ids[0]),
                        ("type_id", "in", rec.code_id.observation_code_ids.ids),
                    ]
                )
                rec.observation_ids = observation
                rec.observation_count = len(observation)
            else:
                rec.observation_ids = None
                rec.observation_count = 0

    @api.onchange("period_type")
    def _onchange_period_type(self):
        if self.period_type == "age" and not self.patient_id.birthdate:
            self.period_type = "date"
            return {
                "warning": {
                    "title": _("Warning!"),
                    "message": _("%s must specify birthday to set onset age")
                    % self.patient_id.name,
                }
            }

    @api.depends("period_start", "period_end")
    def _compute_age(self):
        for rec in self:
            dt = relativedelta(self.period_start, self.patient_id.birthdate)
            rec.age_start = dt.years
            dt = relativedelta(self.period_end, self.patient_id.birthdate)
            rec.age_end = dt.years

    def _inverse_age_start(self):
        for rec in self.filtered(lambda r: r.age_start):
            start = rec.patient_id.birthdate + relativedelta(years=rec.age_start)
            rec.period_start = datetime.combine(start, datetime.min.time())
            rec.period_start_date = start

    def _inverse_age_end(self):
        for rec in self.filtered(lambda r: r.age_end):
            end = rec.partner_id.birthdate + relativedelta(years=rec.age_end)
            rec.period_end = datetime.combine(end, datetime.min.time())
            rec.period_end_date = end

    @api.depends("category_ids")
    def _compute_category(self):
        self.filtered_domain(
            [
                (
                    "category_ids",
                    "child_of",
                    self.env.ref("ni_condition.problem_list_item").id,
                )
            ]
        ).is_problem = True
        self.filtered_domain(
            [
                (
                    "category_ids",
                    "child_of",
                    self.env.ref("ni_condition.encounter_diagnosis").id,
                )
            ]
        ).is_diagnosis = True

    def _inverse_is_problem(self):
        self.filtered_domain([("is_problem", "=", True)]).category_ids = [
            fields.Command.link(self.env.ref("ni_condition.problem_list_item").id)
        ]
        self.filtered_domain([("is_problem", "=", False)]).category_ids = [
            fields.Command.unlink(self.env.ref("ni_condition.problem_list_item").id)
        ]

    def _inverse_is_diagnosis(self):
        self.filtered_domain([("is_diagnosis", "=", True)]).category_ids = [
            fields.Command.link(self.env.ref("ni_condition.encounter_diagnosis").id)
        ]
        self.filtered_domain([("is_diagnosis", "=", False)]).category_ids = [
            fields.Command.unlink(self.env.ref("ni_condition.encounter_diagnosis").id)
        ]

    @api.onchange("code_id")
    def _onchange_code_id(self):
        for rec in self.filtered(lambda r: r.code_id):
            rec.name = rec.code_id.name

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        condition = self
        name = condition.name or condition.code_id.name
        if self._context.get("show_code") and condition.code_id.code:
            name = "[{}] {}".format(name, condition.code_id.code)
        if self._context.get("show_patient"):
            name = "{}: {}".format(condition.patient_id._name_get(), name)
        if self._context.get("show_severity") and condition.severity:
            name = "{}[{}]".format(name, condition.get_severity_label())
        if self._context.get("show_state"):
            name = "{} ({})".format(name, condition.get_state_label())
        return name

    def get_severity_label(self):
        self.ensure_one()
        return dict(self._fields["severity"].selection).get(self.severity)

    def get_state_label(self):
        self.ensure_one()
        return dict(self._fields["clinical_state"].selection).get(self.clinical_state)

    def action_edit(self):
        self.ensure_one()
        view = {
            "name": self.name,
            "res_model": self._name,
            "type": "ir.actions.act_window",
            "target": "current",
            "res_id": self.id,
            "view_type": "form",
            "views": [[False, "form"]],
            "context": self.env.context,
        }
        return view

    def action_remission(self):
        self.write({"clinical_state": "remission", "period_end": fields.Date.today()})
        return True

    def action_resolve(self):
        self.write({"clinical_state": "resolved", "period_end": fields.Date.today()})
        return True

    def action_active(self):
        self.write({"clinical_state": "active", "period_end": False})
        return True

    @property
    def _workflow_name(self) -> str:
        if self.is_diagnosis:
            return _("Diagnosis Encounter")
        elif self.is_problem:
            return _("Problem List Item")
        else:
            return self._description

    @property
    def _workflow_summary(self):
        summary = self.code_id.name
        if self.severity:
            summary = "{} ({})".format(summary, self.get_severity_label())
        if self.verification_id:
            summary = "{} - {}".format(summary, self.verification_id.display_name)
        return summary

    @api.constrains("age_start", "age_end")
    def _check_age(self):
        for rec in self:
            if rec.age_start and rec.age_start > rec.patient_id.age:
                raise UserError(_("Onset age must not be more than patient age"))
            if rec.age_end and rec.age_end > rec.patient_id.age:
                raise UserError(_("Abatement age must not be more than patient age"))
            if rec.age_start and rec.age_end and rec.age_end < rec.age_start:
                raise UserError(_("Abatement age must be more than onset age"))

    @api.constrains("code_id", "system_id")
    def _check_(self):
        for rec in self:
            if rec.code_id and rec.code_id.system_id != rec.system_id:
                rec.system_id = rec.code_id.system_id
