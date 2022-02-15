#  Copyright (c) 2022 Piruin P.

from odoo import fields, models


class ConditionCode(models.Model):
    _inherit = "ni.condition.code"

    survey_id = fields.Many2one(
        "survey.survey",
        "Related Survey",
        domain=[("state", "=", "open"), ("category", "=", "ni_patient")],
        help="Questionnaire associate to this condition",
    )
