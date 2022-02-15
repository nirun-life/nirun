#  Copyright (c) 2021 Piruin P.

from odoo import models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    def write(self, vals):
        state = vals.get("state")
        if state and state == "done":
            self._onchange_state_done()
        return super().write(vals)

    def _onchange_state_done(self):
        conditions = self.env["ni.condition"].sudo()
        for rec in self.filtered(lambda s: s.subject_model == "ni.patient"):
            grade = rec.quizz_grade_id
            if grade and grade.condition_code_id:
                condition = conditions.search(
                    [
                        ("patient_id", "=", rec.patient_id.id),
                        ("code_id", "=", grade.condition_code_id.id),
                    ],
                    limit=1,
                    order="create_date desc",
                )
                vals = rec._prepare_condition_vals()
                if condition:
                    vals["write_uid"] = rec.create_uid
                    condition.update(vals)
                elif grade.condition_state != "resolved":
                    vals["create_uid"] = rec.create_uid
                    conditions.create(vals)

    def _prepare_condition_vals(self, default=None):
        self.ensure_one()
        vals = default or {}
        vals.update(
            {
                "patient_id": self.patient_id.id,
                "encounter_id": self.encounter_id.id,
                "category": "problem-list-item",
                "code_id": self.quizz_grade_id.condition_code_id.id,
                "severity": self.quizz_grade_id.condition_severity,
                "state": self.quizz_grade_id.condition_state,
                "response_ids": [(4, self.id, 0)],
            }
        )
        return vals
