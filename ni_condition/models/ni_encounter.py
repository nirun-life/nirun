#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    condition_ids = fields.One2many(
        "ni.condition", "encounter_id", string="Diagnosis", check_company=True
    )
    condition_prev_ids = fields.One2many(
        "ni.condition",
        string="Previous Diagnosis",
        compute="_compute_condition_prev_ids",
    )
    # Following field is require to make operation on UI work as it should work,
    # Because, UI weird behavior that will send Null `patient_id.condition_problem_code_ids`
    # when created new encounter rec of registered patient, trigger the inverse function to
    # delete all old problems of patient
    problem_code_ids = fields.Many2many(
        "ni.condition.code",
        compute="_compute_problem_code_ids",
        inverse="_inverse_problem_code_ids",
        help="",
    )

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
    def _compute_problem_code_ids(self):
        problem = self.env["ni.condition"].search(
            [
                ("patient_id", "in", self.mapped("patient_id.id")),
                ("is_problem", "=", True),
            ]
        )
        for rec in self:
            problem_ids = problem.filtered_domain(
                [("patient_id", "=", rec.patient_id.id)]
            )
            rec.write(
                {
                    "problem_code_ids": [(4, p.code_id.id, 0) for p in problem_ids],
                }
            )

    def _inverse_problem_code_ids(self):
        for rec in self:
            # remove all condition (problem) that have been removed
            cmd = [
                (2, c.id, 0)
                for c in rec.condition_problem_ids.filtered_domain(
                    [("code_id", "not in", rec.problem_code_ids.ids)]
                )
            ]
            # Then add new condition (problem)
            cmd = cmd + [
                (
                    0,
                    0,
                    {
                        "code_id": p.id,
                        "patient_id": rec.patient_id.id,
                        "encounter_id": rec.encounter_id.id,
                        "is_problem": True,
                    },
                )
                for p in rec.problem_code_ids
                if p not in rec.patient_id.condition_ids.mapped("code_id")
            ]
            if cmd:
                rec.write({"condition_ids": cmd})
