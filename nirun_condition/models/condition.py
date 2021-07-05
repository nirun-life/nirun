#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Condition(models.Model):
    _name = "ni.condition"
    _description = "Condition"
    _inherit = ["period.mixin", "ni.patient.res"]

    name = fields.Char(related="code_id.name", store=True)
    category = fields.Selection(
        [
            ("problem-list-item", "Problem List Item"),
            ("encounter-diagnosis", "Encounter Diagnosis"),
        ],
        required=True,
    )
    code_id = fields.Many2one(
        "ni.condition.code",
        "Condition / Problem",
        required=True,
        ondelete="restrict",
        index=True,
    )
    type_id = fields.Many2one(related="code_id.type_id", string="Type", store=True)
    severity = fields.Selection(
        [("mild", "Mild"), ("moderate", "Moderate"), ("severe", "Severe")],
        tracking=1,
        required=False,
    )
    period_start = fields.Date(default=None)
    state = fields.Selection(
        [
            ("active", "Suffering"),
            ("remission", "Remission"),
            ("resolved", "Resolved"),
        ],
        string="Status",
        copy=False,
        index=True,
        tracking=1,
        default="active",
    )
    recurrence = fields.Boolean()
    gender = fields.Selection(related="patient_id.gender", store=True)
    note = fields.Text()

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        condition = self
        name = condition.name or condition.code_id.name
        if self._context.get("show_patient"):
            name = "{} : {}".format(condition.patient_id._name_get(), name)
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

    @api.onchange("encounter_id")
    def _onchange_encounter_id(self):
        self.ensure_one()
        self.category = (
            "encounter-diagnosis" if self.encounter_id else "problem-list-item"
        )

    _sql_constraints = [
        (
            "condition_encounter__uniq",
            "unique (patient_id, code_id, encounter_id)",
            "Patient already have this condition!",
        ),
    ]
