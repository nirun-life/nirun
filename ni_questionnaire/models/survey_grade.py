#  Copyright (c) 2024 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SurveyGrade(models.Model):
    _inherit = "survey.grade"
    _order = "gender,age_low,low desc"

    gender = fields.Selection([("male", "Male"), ("female", "Female")], required=False)
    age_low = fields.Integer(default=0)
    age_high = fields.Integer(default=200)

    _sql_constraints = [
        (
            "name_uniq",
            "unique (survey_id, name, gender, age_low)",
            "A grading name must be unique!",
        )
    ]

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

    @api.constrains("low", "high")
    def _validate_low_high(self):
        for rec in self:
            if not (0.0 <= rec.low <= 100.0):
                raise ValidationError(
                    _("%s low value must be in between 0.0-100.0") % rec.name
                )
            if not (0.0 <= rec.high <= 100.0):
                raise ValidationError(
                    _("%s high value must be in between 0.0-100.0") % rec.name
                )
            if rec.low > rec.high:
                raise ValidationError(
                    _("%s is not a valid range (%s >= %s)")
                    % (rec.name, rec.low, rec.high)
                )

            grade_id = rec.search(
                [
                    ("survey_id", "in", [rec.survey_id.id, False]),
                    ("gender", "=", rec.gender),
                    ("age_low", "=", rec.age_low),
                    ("low", "<", rec.high),
                    ("high", ">", rec.low),
                    ("id", "!=", rec.id),
                ],
                limit=1,
            )
            if grade_id:
                raise ValidationError(
                    _("%s is overlapping with %s") % (rec.name, grade_id.name)
                )
