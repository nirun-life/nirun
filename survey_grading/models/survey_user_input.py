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

    @api.depends(
        "scoring_percentage",
        "scoring_total",
        "survey_id.grading_basis",
        "user_input_line_ids.suggested_answer_id",
    )
    def _compute_grade_id(self):
        for rec in self:
            rec.grade_id = rec._quizz_grade()

    def _grading_value(self):
        """Value the grade ranges are compared against."""
        self.ensure_one()
        if self.survey_id.grading_basis == "score":
            return self.scoring_total
        return self.scoring_percentage

    def _grade_candidates(self):
        """Grades that apply to this response.

        Grades scoped to a selected answer take precedence over unscoped ones, which
        is how a survey holds several sets of ranges with a different maximum score.
        """
        self.ensure_one()
        answers = self.user_input_line_ids.suggested_answer_id
        scoped = self.grade_ids.filtered(lambda g: g.triggering_answer_ids & answers)
        return scoped or self.grade_ids.filtered(lambda g: not g.triggering_answer_ids)

    def grade_reference(self):
        """The bands this response could have landed in, best first.

        Public because the completion page renders it.
        """
        self.ensure_one()
        return self._grade_candidates().sorted("low", reverse=True)

    def grade_scale(self):
        """This response's value against the top of the scale it was graded on.

        Not `total_possible_score`: that is the whole survey's maximum, and it
        overstates the scale whenever conditional questions drop out - the case
        `grading_basis = score` exists for. The candidate bands are authored per
        gate, so their highest bound is the ceiling this response was actually
        measured against. Empty when there is no such ceiling.
        """
        self.ensure_one()
        top = max(self._grade_candidates().mapped("high"), default=0)
        if not top:
            return ""
        unit = "" if self.survey_id.grading_basis == "score" else "%"
        return "%g / %g%s" % (self._grading_value(), top, unit)

    def grade_conditions(self):
        """Why these bands and not another set, for the reader of that table.

        Extended by ni_questionnaire with the patient traits it grades on.
        """
        self.ensure_one()
        answers = self.user_input_line_ids.suggested_answer_id
        return (answers & self._grade_candidates().triggering_answer_ids).mapped(
            "value"
        )

    def _quizz_grade(self):
        self.ensure_one()
        value = self._grading_value()
        for grade in self._grade_candidates():
            if grade.is_cover(value):
                return grade
        return None
