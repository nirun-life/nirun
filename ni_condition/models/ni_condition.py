#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models


class Condition(models.Model):
    _name = "ni.condition"
    _description = "Condition"
    _inherit = ["ni.period.mixin", "ni.patient.res"]
    _workflow_occurrence = "create_date"

    def _get_default_condition_class(self):
        return (
            self.env["ni.condition.class"].search([], order="sequence", limit=1).id
            or None
        )

    name = fields.Char(related="code_id.name", store=True)

    is_problem = fields.Boolean("Chronic", help="Save on Problem List Item")
    is_diagnosis = fields.Boolean(
        "Diagnosis", help="Condition that relate to encounter"
    )

    code_id = fields.Many2one(
        "ni.condition.code",
        "Name",
        required=True,
        ondelete="restrict",
        index=True,
    )
    code = fields.Char(related="code_id.code", store=True)
    class_id = fields.Many2one(
        "ni.condition.class",
        default=lambda self: self._get_default_condition_class(),
        required=True,
    )
    severity = fields.Selection(
        [("mild", "Mild"), ("moderate", "Moderate"), ("severe", "Severe")],
        required=False,
    )
    period_start = fields.Datetime("Onset", default=None)
    period_start_date = fields.Date("Onset Date", default=None)
    period_end = fields.Datetime("Abatement")
    period_end_date = fields.Datetime("Abatement Date")
    clinical_state = fields.Selection(
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
        default="active",
    )
    verification_id = fields.Many2one("ni.condition.verification")
    recurrence = fields.Boolean()
    note = fields.Text()
    diagnosis_ids = fields.One2many(
        "ni.encounter.diagnosis", "condition_id", readonly=True
    )

    _sql_constraints = [
        (
            "patient_id_code_id_uniq",
            "unique (patient_id, code_id)",
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

    @api.onchange("code_id")
    def onchange_code_id(self):
        if self.code_id.class_id:
            self.class_id = self.code_id.class_id

    @property
    def _workflow_name(self) -> str:
        if self.is_diagnosis:
            return _("Diagnosis")
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
