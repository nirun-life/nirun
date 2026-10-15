#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class Survey(models.Model):
    _inherit = "survey.survey"

    grade_ids = fields.One2many("survey.grade", "survey_id")
    grading_basis = fields.Selection(
        [("percentage", "Percentage"), ("score", "Points")],
        default="percentage",
        # Not required: a NOT NULL column on survey.survey would break core
        # survey's own tests. Readers treat an empty value as "percentage".
        help="Compare grade ranges against the score percentage, or against the raw "
        "total score. Use Points when the maximum score varies between responses, "
        "e.g. when conditional questions drop out of the scoring.",
    )
