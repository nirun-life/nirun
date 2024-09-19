#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class SurveyQuestion(models.Model):
    _inherit = "survey.question"

    observation_code_id = fields.Many2one("ni.observation.type", "Observation")
    observation_answer_type = fields.Selection(
        [("score", "Score"), ("value", "Value")],
        "Value type",
        default="score",
        required=True,
    )
