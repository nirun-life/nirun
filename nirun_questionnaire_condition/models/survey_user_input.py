#  Copyright (c) 2021 Piruin P.

from odoo import models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    def write(self, vals):
        state = vals.get("state")
        if state and state == "done":
            self.onchange_state_done()
        return super().write(vals)

    def onchange_state_done(self):
        condition = self.env["ni.condition"].sudo()
        for rec in self.filtered(lambda s: s.subject_model == "ni.patient"):
            grade = rec.quizz_grade_id
            if grade and grade.condition_id:
                vals = {
                    "patient_id": rec.patient_id.id,
                    "encounter_id": rec.encounter_id.id,
                    "category": "encounter-diagnosis",
                    "code_id": grade.condition_id.id,
                    "severity": grade.condition_severity,
                }
                condition.create(vals)
