#  Copyright (c) 2026 NSTDA
from odoo import _, api, fields, models


class ImmunizationSummary(models.Model):
    _name = "ni.immunization.summary"
    _description = "Immunization Disease Summary"
    _auto = False
    _rec_name = "target_disease_id"
    _order = "target_disease_id"

    patient_id = fields.Many2one("ni.patient", readonly=True)
    target_disease_id = fields.Many2one(
        "ni.immunization.target.disease", string="Disease", readonly=True
    )
    protection_status = fields.Selection(
        [
            ("not-protected", "Not Protected"),
            ("partial", "Partial"),
            ("protected", "Protected"),
        ],
        string="Status",
        readonly=True,
    )
    last_evaluation = fields.Datetime("Last Evaluation", readonly=True)
    last_immunization = fields.Date("Last Immunization", readonly=True)
    dose_count = fields.Integer("Doses", readonly=True, group_operator="max")
    series_doses = fields.Integer("Required", readonly=True, group_operator="max")
    dose_progress = fields.Char("Doses", readonly=True)
    evaluation_ids = fields.Many2many(
        "ni.immunization.evaluation",
        compute="_compute_evaluation_ids",
        string="History",
    )

    @api.depends("patient_id", "target_disease_id")
    def _compute_evaluation_ids(self):
        Evaluation = self.env["ni.immunization.evaluation"]
        for rec in self:
            rec.evaluation_ids = Evaluation.search(
                [
                    ("patient_id", "=", rec.patient_id.id),
                    ("target_disease_id", "=", rec.target_disease_id.id),
                ],
                order="dose_number desc",
            )

    def init(self):
        self.env.cr.execute(
            """
            CREATE INDEX IF NOT EXISTS ni_immunization_evaluation_summary_idx
            ON ni_immunization_evaluation (patient_id, target_disease_id, dose_number DESC, id DESC)
            INCLUDE (dose_status, series_doses, occurrence, immunization_date)
            """
        )
        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW ni_immunization_summary AS (
                SELECT DISTINCT ON (patient_id, target_disease_id)
                    id,
                    patient_id,
                    target_disease_id,
                    CASE
                        WHEN dose_status != 'valid' THEN 'not-protected'
                        WHEN dose_number >= series_doses THEN 'protected'
                        ELSE 'partial'
                    END AS protection_status,
                    occurrence AS last_evaluation,
                    immunization_date AS last_immunization,
                    dose_number AS dose_count,
                    series_doses,
                    CONCAT(dose_number::text, ' / ', series_doses::text) AS dose_progress
                FROM ni_immunization_evaluation
                ORDER BY patient_id, target_disease_id, dose_number DESC, id DESC
            )
        """
        )

    def action_add_evaluation(self):
        ctx = self.env.context
        return {
            "type": "ir.actions.act_window",
            "name": _("Add Dose"),
            "res_model": "ni.immunization.evaluation",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_patient_id": self.patient_id.id,
                "default_target_disease_id": self.target_disease_id.id,
                "default_encounter_id": ctx.get("default_encounter_id"),
            },
        }
