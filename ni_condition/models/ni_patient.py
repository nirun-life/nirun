#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    condition_ids = fields.One2many(
        "ni.condition", "patient_id", string="Condition", check_company=True
    )
    condition_code_ids = fields.Many2many(
        "ni.condition.code",
        compute="_compute_condition_problem_ids",
        inverse="_inverse_condition_problem_ids",
    )
    condition_problem_ids = fields.One2many(
        "ni.condition",
        "patient_id",
        "Problem",
        compute="_compute_condition_problem_ids",
    )
    problem_count = fields.Integer(compute="_compute_condition_problem_ids")
    condition_report_ids = fields.One2many("ni.condition.latest", "patient_id")

    def _inverse_condition_problem_ids(self):
        # This inverse function is good for simple version if require detail in condition
        # 'condition_problem_ids' should always set as READONLY
        # NOTE this also not work as expected on encounter form
        for rec in self:
            cmd = []
            rmv = [
                fields.Command.delete(condition.id)
                for condition in rec.condition_ids.filtered(lambda c: c.is_problem)
                if condition.code_id not in rec.condition_code_ids
            ]
            for code in rec.condition_code_ids:
                if not rec.condition_ids.filtered_domain([("code_id", "=", code.id)]):
                    cmd += [
                        fields.Command.create(
                            {
                                "name": code.name,
                                "code_id": code.id,
                                "is_problem": True,
                            }
                        )
                    ]
            if cmd or rmv:
                cmd = rmv + cmd
                rec.condition_ids = cmd

    @api.depends("condition_ids")
    def _compute_condition_problem_ids(self):
        for rec in self:
            problem = self.env["ni.condition"].search(
                [("patient_id", "=", rec.id), ("is_problem", "=", True)]
            )
            rec.condition_problem_ids = problem
            rec.problem_count = len(problem)
            rec.condition_code_ids = problem.mapped("code_id")

    def action_condition(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_patient_id": self[0].id,
            }
        )
        view = {
            "name": _("Problem List"),
            "res_model": "ni.condition",
            "type": "ir.actions.act_window",
            "target": "current",
            "view_mode": "tree,form",
            "domain": [("patient_id", "=", self.patient_id.id)],
            "context": ctx,
        }
        return view
