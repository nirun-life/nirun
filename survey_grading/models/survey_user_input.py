#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    grade_ids = fields.One2many(related="survey_id.grade_ids", string="Possible grades")
    quizz_grade_id = fields.Many2one(
        "survey.grade",
        compute="_compute_quizz_grade_id",
        store=True,
        index=True,
        copy=False,
    )
    quizz_grade = fields.Char(related="quizz_grade_id.name")

    @api.depends("quizz_score")
    def _compute_quizz_grade_id(self):
        for rec in self:
            rec.quizz_grade_id = rec._quizz_grade()

    def _quizz_grade(self):
        self.ensure_one()
        for grade in self.grade_ids:
            if grade.is_cover(self.quizz_score):
                return grade
        return None
