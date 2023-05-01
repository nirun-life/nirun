#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    condition_ids = fields.One2many(
        "ni.condition", "patient_id", string="Condition", check_company=True
    )
    condition_problem_ids = fields.One2many(
        "ni.condition",
        "patient_id",
        "Problem",
        compute="_compute_condition_problem_ids",
        inverse="_inverse_condition_problem_ids",
        readonly=False,
    )
    condition_report_ids = fields.One2many("ni.condition.latest", "patient_id")

    @api.depends("condition_ids")
    def _compute_condition_problem_ids(self):
        problem = self.env["ni.condition"].search(
            [("patient_id", "in", self.ids), ("is_problem", "=", True)]
        )
        for rec in self:
            problem_ids = problem.filtered_domain([("patient_id", "=", rec.id)])
            added_code = []
            cmd = []
            for p in problem_ids:
                if p.code_id.id not in added_code:
                    cmd.append((4, p.id))
                    added_code.append(p.code_id.id)
            rec.write({"condition_problem_ids": cmd})

    def _inverse_condition_problem_ids(self):
        for rec in self:
            # remove all condition (problem) that have been removed
            cmd = [
                (2, c.id, 0)
                for c in rec.condition_ids.filtered_domain([("is_problem", "=", True)])
                if c.is_problem is True and c not in rec.condition_problem_ids
            ]
            # Then add new condition (problem)
            cmd = cmd + [
                (0, 0, p.copy_data()[0])
                for p in rec.condition_problem_ids
                if p not in rec.condition_ids
            ]
            if cmd:
                rec.write({"condition_ids": cmd})
