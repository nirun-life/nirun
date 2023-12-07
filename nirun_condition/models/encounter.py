#  Copyright (c) 2021-2023. NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    condition_ids = fields.One2many(
        "ni.condition", "encounter_id", string="Diagnosis", check_company=True
    )
    condition_display = fields.Char(compute="_compute_condition_display")
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
    condition_report_ids = fields.One2many(related="patient_id.condition_report_ids")

    @api.depends("patient_id")
    def _compute_condition_prev_ids(self):
        conditions = self.env["ni.condition"]
        for rec in self:
            rec.condition_prev_ids = conditions.search(
                [
                    ("patient_id", "=", self.patient_id.id),
                    ("encounter_id", "!=", rec.id),
                    ("is_diagnosis", "=", True),
                ],
                order="encounter_id desc",
            )

    @api.depends("condition_ids")
    def _compute_condition_display(self):
        for rec in self:
            rec.condition_display = ", ".join(rec.condition_report_ids.mapped("name"))
