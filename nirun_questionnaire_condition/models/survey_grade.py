#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class SurveyGrade(models.Model):
    _inherit = "survey.grade"

    condition_code_id = fields.Many2one("ni.condition.code")
    condition_severity = fields.Selection(
        [("mild", "Mild"), ("moderate", "Moderate"), ("severe", "Severe")]
    )
    condition_state = fields.Selection(
        [("active", "Suffering"), ("remission", "Remission"), ("resolved", "Resolved")]
    )
