#  Copyright (c) 2021-2023. NSTDA

from odoo import _, api, fields, models


class Condition(models.Model):
    _name = "ni.condition"
    _description = "Condition"
    _inherit = ["period.mixin", "ni.workflow.event.mixin"]
    _workflow_occurrence = "create_date"

    def _get_default_condition_class(self):
        return (
            self.env["ni.condition.cls"].search([], order="sequence", limit=1).id
            or None
        )

    name = fields.Char(related="code_id.name", store=True)
    category = fields.Selection(
        [
            ("problem-list-item", "Problem List Item"),
            ("encounter-diagnosis", "Encounter Diagnosis"),
        ],
        required=True,
        help="Deprecated",
    )
    is_problem = fields.Boolean("Problem List Item")
    is_diagnosis = fields.Boolean("Encounter Diagnosis")
    code_id = fields.Many2one(
        "ni.condition.code",
        "Name",
        required=True,
        ondelete="restrict",
        index=True,
    )
    classification_id = fields.Many2one(
        "ni.condition.cls",
        default=lambda self: self._get_default_condition_class(),
        required=True,
    )
    severity = fields.Selection(
        [("mild", "Mild"), ("moderate", "Moderate"), ("severe", "Severe")],
        tracking=1,
        required=False,
    )
    period_start = fields.Date("Onset Date", default=None)
    period_end = fields.Date("Abatement Date")
    state = fields.Selection(
        [
            ("active", "Suffering"),
            ("recurrence", "Recurrence "),
            ("relapse", "Relapse"),
            ("inactive", "Inactive"),
            ("remission", "Remission"),
            ("resolved", "Resolved"),
        ],
        string="Status",
        copy=False,
        index=True,
        tracking=1,
        default="active",
    )
    verification_id = fields.Many2one("ni.condition.verification")
    recurrence = fields.Boolean()
    note = fields.Text()

    create_date = fields.Datetime("Recorded", readonly=True)
    create_uid = fields.Many2one("res.users", "Recorder", readonly=True)

    _sql_constraints = [
        (
            "condition_encounter__uniq",
            "unique (patient_id, code_id, encounter_id)",
            "Patient already have this condition!",
        ),
    ]

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
        return dict(self._fields["state"].selection).get(self.state)

    def get_verification_label(self):
        self.ensure_one()
        return dict(self._fields["verification"].selection).get(self.verification)

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
        self.write({"state": "remission", "period_end": fields.Date.today()})
        return True

    def action_resolve(self):
        self.write({"state": "resolved", "period_end": fields.Date.today()})
        return True

    def action_active(self):
        self.write({"state": "active", "period_end": False})
        return True

    @api.onchange("code_id")
    def onchange_code_id(self):
        if self.code_id.classification_id:
            self.classification_id = self.code_id.classification_id

    @property
    def _workflow_name(self) -> str:
        if self.is_diagnosis:
            return _("Diagnosis")
        elif self.is_problem:
            return _("Chronic")
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
