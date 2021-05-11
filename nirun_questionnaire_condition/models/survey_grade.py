#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class SurveyGrade(models.Model):
    _inherit = "survey.grade"

    condition_id = fields.Many2one("ni.condition")
    condition_severity = fields.Selection(
        [("mild", "Mild"), ("moderate", "Moderate"), ("severe", "Severe")],
        default="mild",
        tracking=1,
    )
