#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class PatientCondition(models.Model):
    _name = "ni.patient.condition"
    _description = "Patient's Condition"
    _inherit = ["period.mixin", "mail.thread"]
    category = fields.Selection(
        [
            ("problem-list-item", "Problem list item"),
            ("encounter-diagnosis", "Encounter Diagnosis"),
        ]
    )
    patient_id = fields.Many2one("ni.patient", required=True, index=True)
    condition_id = fields.Many2one(
        "ni.condition", required=True, ondelete="restrict", index=True
    )
    condition_category_id = fields.Many2one(
        related="condition_id.category_id", string="Condition Category", required=False
    )
    encounter_id = fields.Many2one(
        "ni.encounter",
        required=False,
        help="Encounter this condition is part of",
        index=True,
    )
    severity = fields.Selection(
        [("mild", "Mild"), ("moderate", "Moderate"), ("severe", "Severe")],
        default="mild",
        tracking=1,
    )
    state = fields.Selection(
        [
            ("active", "Active"),
            ("recurrence", "recurrence"),
            ("relapse", "relapse"),
            ("inactive", "Inactive"),
            ("remission", "remission"),
            ("resolved", "resolved"),
        ],
        string="Status",
        copy=False,
        index=True,
        tracking=1,
        default="active",
    )

    @api.onchange("encounter_id")
    def _onchange_encounter_id(self):
        self.ensure_one()
        self.category = (
            "encounter-diagnosis" if self.encounter_id else "problem-list-item"
        )

    _sql_constraints = [
        (
            "patient_condition_encounter__uniq",
            "unique (patient_id, condition_id, encounter_id)",
            "Patient already have this condition!",
        ),
    ]
