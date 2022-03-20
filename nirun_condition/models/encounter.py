#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    condition_ids = fields.One2many(
        "ni.condition", "encounter_id", string="Diagnosis", check_company=True
    )
    condition_problem_ids = fields.One2many(
        related="patient_id.condition_problem_ids", readonly=False
    )
    condition_prev_ids = fields.One2many(
        "ni.condition",
        string="Previous Diagnosis",
        compute="_compute_condition_prev_ids",
    )
    condition_ref = fields.Selection(
        [("problem", "Problem"), ("previous", "Previous Diagnosis")],
        default="problem",
        store=False,
    )

    @api.depends("patient_id")
    def _compute_condition_prev_ids(self):
        conditions = self.env["ni.condition"]
        for rec in self:
            rec.condition_prev_ids = conditions.search(
                [
                    ("patient_id", "=", self.patient_id.id),
                    ("encounter_id", "!=", rec.id),
                    ("category", "=", "encounter-diagnosis"),
                ],
                order="encounter_id desc",
            )
