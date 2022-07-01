#  Copyright (c) 2021 NSTDA

from odoo import models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    def write(self, vals):
        state = vals.get("state")
        if state and state == "done":
            self.add_to_group()
        return super().write(vals)

    def add_to_group(self):
        for rec in self.filtered(lambda s: s.subject_model == "ni.patient"):
            grade = rec.quizz_grade_id
            if grade and grade.patient_group_id:
                group_sudo = grade.patient_group_id.sudo()
                group_sudo.patient_ids = [(4, rec.subject_id)]
                if group_sudo.select == "single":
                    group_sudo.get_sibling_ids().write(
                        {"patient_ids": [(3, rec.subject_id)]}
                    )
