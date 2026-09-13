#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SurveyGrade(models.Model):
    _name = "survey.grade"
    _description = "Survey Scoring Grade"
    _order = "survey_id, high DESC"

    survey_id = fields.Many2one(
        "survey.survey", index=True, required=True, ondelete="cascade"
    )
    scoring_success_min = fields.Float(related="survey_id.scoring_success_min")
    grading_basis = fields.Selection(related="survey_id.grading_basis")

    name = fields.Char("Grade", index=True, translate=True, required=True)
    low = fields.Float(
        "Low", default=0.0, help="Lowest score of this grade (Inclusive)"
    )
    high = fields.Float(
        "High",
        default=100.0,
        help="Highest score of this grade, "
        "Inclusive but Exclusive for next lesser grade",
    )
    triggering_answer_ids = fields.Many2many(
        "survey.question.answer",
        string="When Answered",
        domain="[('question_id.survey_id', '=', survey_id)]",
        help="Use this grade only for responses that selected one of these answers. "
        "Leave empty to use it for every response.",
    )
    passing_grade = fields.Boolean(compute="_compute_passing_grade", default=False)
    color_class = fields.Selection(
        [
            ("text", "Text"),
            ("primary", "Primary"),
            ("success", "Success"),
            ("info", "Info"),
            ("warning", "Warning"),
            ("danger", "Danger"),
            ("muted", "Muted"),
        ],
        default="text",
        required=True,
        help="Bootstrap's classes to change the appearance of "
        "this grade's badge at survey result screen",
    )

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        rec = self
        name = rec.name or ""
        if self._context.get("show_score_range"):
            name = "%s [%d-%d]" % (name, rec.low, rec.high)
        return name

    def is_cover(self, value):
        self.ensure_one()
        return self.low <= value <= self.high

    def _scope_key(self):
        """Values that make two grades independent of each other.

        Grades sharing a scope key must have a unique name and must not overlap;
        grades of different scopes are free to overlap. Extended by ni_questionnaire
        to add the patient's gender and age range.
        """
        self.ensure_one()
        return (tuple(sorted(self.triggering_answer_ids.ids)),)

    @api.depends("scoring_success_min", "low", "grading_basis")
    def _compute_passing_grade(self):
        for rec in self:
            rec.passing_grade = (
                rec.grading_basis != "score" and rec.low >= rec.scoring_success_min
            )

    @api.constrains("name", "low", "high", "triggering_answer_ids")
    def _validate_low_high(self):
        for rec in self:
            if rec.grading_basis != "score" and not (
                0.0 <= rec.low <= 100.0 and 0.0 <= rec.high <= 100.0
            ):
                raise ValidationError(
                    _("%s low and high value must be in between 0.0-100.0") % rec.name
                )
            if rec.low > rec.high:
                raise ValidationError(
                    _("%s is not a valid range (%s >= %s)")
                    % (rec.name, rec.low, rec.high)
                )

            scope = rec._scope_key()
            for other in rec.survey_id.grade_ids - rec:
                if other._scope_key() != scope:
                    continue
                if other.name == rec.name:
                    raise ValidationError(
                        _("A grading name must be unique! (%s)") % rec.name
                    )
                if other.low < rec.high and other.high > rec.low:
                    raise ValidationError(
                        _("%s is overlapping with %s") % (rec.name, other.name)
                    )
