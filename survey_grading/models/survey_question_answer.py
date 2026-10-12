#  Copyright (c) 2021-2023 NSTDA

from odoo import api, models


class SurveyQuestionAnswer(models.Model):
    _inherit = "survey.question.answer"

    @api.depends(
        "value",
        "question_id.question_type",
        "question_id.title",
        "matrix_question_id",
        "matrix_question_id.title",
    )
    @api.depends_context("show_question")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        if self.env.context.get("show_question"):
            for rec in self:
                question = rec.question_id or rec.matrix_question_id
                rec.display_name = f"{question.title}: {rec.value}"
        return res
