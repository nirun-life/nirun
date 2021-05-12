#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SurveyGrade(models.Model):
    _name = "survey.grade"
    _description = "Survey Scoring Grade"
    _order = "survey_id, high DESC"

    survey_id = fields.Many2one(
        "survey.survey", index=True, required=True, ondelete="cascade"
    )
    passing_score = fields.Float(related="survey_id.passing_score")

    name = fields.Char("Grade", index=True, translate=True, required=True)
    low = fields.Float(
        "Low (%)", default=0.0, help="Lowest percentage of score (Inclusive)"
    )
    high = fields.Float(
        "High (%)", default=100.0, help="Highest percentage of score (Inclusive)"
    )
    passing_grade = fields.Boolean(compute="_compute_passing_grade", default=False)

    def name_get(self):
        return [(rec.id, rec._name_get()) for rec in self]

    def _name_get(self):
        rec = self
        name = rec.name or ""
        if self._context.get("show_score_range"):
            name = "%s [%d-%d]" % (name, rec.low, rec.high)
        return name

    def is_cover(self, value):
        return self.low <= value <= self.high

    @api.depends("passing_score", "low")
    def _compute_passing_grade(self):
        for rec in self:
            rec.passing_grade = rec.low >= rec.passing_score

    @api.constrains("low", "high")
    def _validate_low_high(self):
        for rec in self:
            if rec.low > rec.high:
                raise ValidationError(_("low value must not be more than high value"))
