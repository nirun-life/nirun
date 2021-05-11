#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    quizz_score_raw = fields.Float(
        "Score", compute="_compute_quizz_score", store=True, compute_sudo=True
    )
    quizz_score_total = fields.Float(
        "Total Score", compute="_compute_quizz_score", store=False, compute_sudo=True
    )

    @api.depends("user_input_line_ids.answer_score", "user_input_line_ids.question_id")
    def _compute_quizz_score(self):
        for rec in self:
            rec.quizz_score_total = sum(
                [
                    max_score if max_score > 0 else 0
                    for max_score in rec.question_ids.mapped("score")
                ]
            )
            if rec.quizz_score_total == 0:
                rec.quizz_score = 0
                rec.quizz_score_raw = 0
            else:
                rec.quizz_score_raw = sum(
                    rec.user_input_line_ids.mapped("answer_score")
                )
                score = (rec.quizz_score_raw / rec.quizz_score_total) * 100
                rec.quizz_score = round(score, 2) if score > 0 else 0
