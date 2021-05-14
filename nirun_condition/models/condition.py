#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Condition(models.Model):
    _name = "ni.condition"
    _description = "Condition"
    _inherit = ["period.mixin", "ni.patient.res"]

    category = fields.Selection(
        [
            ("problem-list-item", "Problem list item"),
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
