#  Copyright (c) 2021 Piruin P.

from odoo import fields, models, tools


class PatientConditionLatest(models.Model):
    _name = "ni.patient.condition.latest"
    _inherit = ["period.mixin"]
    _auto = False

    patient_id = fields.Many2one("ni.patient", readonly=True, index=True)
    condition_id = fields.Many2one(
        "ni.condition", readonly=True, required=True, index=True
    )
    condition_category_id = fields.Many2one(
        related="condition_id.category_id", readonly=True,
    )
    encounter_id = fields.Many2one("ni.encounter", readonly=True)
    start = fields.Date(readonly=True)
    end = fields.Date(readonly=True)
    state = fields.Selection(
        [
            ("active", "Active"),
            ("recurrence", "recurrence"),
            ("relapse", "relapse"),
            ("inactive", "Inactive"),
            ("remission", "remission"),
            ("resolved", "resolved"),
        ],
        readonly=True,
    )
    severity = fields.Selection(
        [("mild", "Mild"), ("moderate", "Moderate"), ("severe", "Severe")], readonly=1
    )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
           SELECT *
            FROM ni_patient_condition
            WHERE id IN (
                SELECT max(id)
                FROM ni_patient_condition
                GROUP BY patient_id, condition_id
            )
        )
        """
            % self._table
        )
