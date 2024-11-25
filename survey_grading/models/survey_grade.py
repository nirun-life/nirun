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

    name = fields.Char("Grade", index=True, translate=True, required=True)
    low = fields.Float(
        "Low (%)", default=0.0, help="Lowest percentage of score (Inclusive)"
    )
    high = fields.Float(
        "High (%)",
        default=100.0,
        help="Highest percentage of score, "
        "Inclusive but Exclusive for next lesser grade",
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
    _sql_constraints = [
        ("name_uniq", "unique (survey_id, name)", "A grading name must be unique!")
    ]

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

    @api.depends("scoring_success_min", "low")
    def _compute_passing_grade(self):
        for rec in self:
            rec.passing_grade = rec.low >= rec.scoring_success_min

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
