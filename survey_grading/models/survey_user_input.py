#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    grade_ids = fields.One2many(related="survey_id.grade_ids", string="Possible grades")
    grade_id = fields.Many2one(
        "survey.grade",
        compute="_compute_grade_id",
        store=True,
        index=True,
        copy=False,
    )
    grade = fields.Char(related="grade_id.name")

    @api.depends("scoring_percentage")
    def _compute_grade_id(self):
        for rec in self:
            rec.grade_id = rec._quizz_grade()

    def _quizz_grade(self):
        self.ensure_one()
        for grade in self.grade_ids:
            if grade.is_cover(self.scoring_percentage):
                return grade
        return None
