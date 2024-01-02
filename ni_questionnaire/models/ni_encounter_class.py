#  Copyright (c) 2023 NSTDA

from odoo import fields, models


class EncounterClassification(models.Model):
    _inherit = "ni.encounter.class"

    survey_id = fields.Many2one(
        "survey.survey",
        "Questionnaire",
        help="Questionnaire relate for this class of encounter",
        groups="survey.group_survey_user",
        domain="[('subject_type', 'in', ['ni.encounter', 'ni.patient'])]",
    )
