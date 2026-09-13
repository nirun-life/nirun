#  Copyright (c) 2024 NSTDA

from odoo import fields, models


class SurveyGrade(models.Model):
    _inherit = "survey.grade"
    _order = "gender,age_low,low desc"

    gender = fields.Selection([("male", "Male"), ("female", "Female")], required=False)
    age_low = fields.Integer(default=0)
    age_high = fields.Integer(default=200)
    subject_type = fields.Selection(related="survey_id.subject_type")
    observation_id = fields.Many2one(related="survey_id.observation_type_id")
    interpretation_id = fields.Many2one(
        "ni.observation.interpretation",
        help="Interpretation given to the observation derived from this response, "
        "instead of looking the score up in the observation's reference ranges.",
    )

    def grade_for(self, age=0, gender=None):
        return self.filtered_domain(
            [
                "|",
                ("gender", "=", gender),
                ("gender", "=", False),
                ("age_low", "<=", age),
                ("age_high", ">=", age),
            ]
        )

    def _scope_key(self):
        return super()._scope_key() + (self.gender, self.age_low, self.age_high)
