#  Copyright (c) 2021-2023. NSTDA

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    condition_ids = fields.One2many(
        "ni.condition", "patient_id", string="Problem", check_company=True
    )
    condition_report_ids = fields.One2many("ni.condition.latest", "patient_id")
    condition_problem_ids = fields.One2many(
        "ni.condition",
        "patient_id",
        "Problem",
        compute="_compute_condition_problem_ids",
        inverse="_inverse_condition_problem_ids",
        readonly=False,
    )
    condition_problem_display = fields.Char(compute="_compute_problem_display")

    @api.depends("condition_problem_ids")
    def _compute_problem_display(self):
        for rec in self:
            rec.condition_problem_display = ", ".join(
                rec.condition_problem_ids.mapped("name")
            )

    @api.depends("condition_ids")
    def _compute_condition_problem_ids(self):
        problem = self.env["ni.condition"].search(
            [("patient_id", "in", self.ids), ("is_problem", "=", True)]
        )
        for rec in self:
            rec.condition_problem_ids = problem.filtered_domain(
                [("patient_id", "=", rec.id)]
            )

    def _inverse_condition_problem_ids(self):
        for rec in self:
            cmd = [
                (2, c.id, 0)
                for c in rec.condition_ids
                if c not in rec.condition_problem_ids
            ]
            cmd = cmd + [
                (0, 0, p.copy_data()[0])
                for p in rec.condition_problem_ids
                if p not in rec.condition_ids
            ]
            rec.write({"condition_ids": cmd})
