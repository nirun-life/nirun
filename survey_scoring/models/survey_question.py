#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    score = fields.Float(compute="_compute_score", store=True)

    @api.depends("labels_ids.answer_score")
    def _compute_score(self):
        for rec in self:
            if not rec.labels_ids:
                rec.score = 0
            elif rec.question_type == "simple_choice":
                rec.score = self.get_max_score_in(rec.labels_ids).answer_score
            elif rec.question_type == "matrix" and rec.matrix_subtype == "simple":
                rec.score = self.get_max_score_in(rec.labels_ids).answer_score * len(
                    rec.labels_ids_2
                )
            elif rec.question_type == "matrix" and rec.matrix_subtype == "multiple":
                rec.score = rec.sum_answer_score * len(rec.labels_ids_2)
            else:
                rec.score = rec.sum_answer_score

    @property
    def sum_answer_score(self):
        self.ensure_one()
        return sum(
            [
                answer_score if answer_score > 0 else 0
                for answer_score in self.mapped("labels_ids.answer_score")
            ]
        )

    @api.model
    def get_max_score_in(self, labels):
        if len(labels) == 1:
            return labels[0]
        else:
            m = self.get_max_score_in(labels[1:])
            return m if m.answer_score > labels[0].answer_score else labels[0]
