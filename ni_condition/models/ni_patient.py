#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models


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
    )
    condition_report_ids = fields.One2many("ni.condition.latest", "patient_id")

    @api.depends("condition_ids")
    def _compute_condition_problem_ids(self):
        for rec in self:
            problem = self.env["ni.condition"].search(
                [("patient_id", "=", rec.id), ("is_problem", "=", True)]
            )
            rec.condition_problem_ids = problem

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
