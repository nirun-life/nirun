#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class SurveyQuestionAnswer(models.Model):
    _inherit = "survey.question.answer"

    def name_get(self):
        if not self._context.get("show_question"):
            return super().name_get()
        return [
            (
                rec.id,
                "%s: %s"
                % ((rec.question_id or rec.matrix_question_id).title, rec.value),
            )
            for rec in self
        ]
