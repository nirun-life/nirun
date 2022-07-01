#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class PatientGroup(models.Model):
    _inherit = "ni.patient.group"

    survey_id = fields.Many2one(
        "survey.survey",
        string="Questionnaire",
        domain=[("category", "=", "ni_patient")],
        help="Questionnaire relate for this class of encounter",
    )
    parent_survey_id = fields.Many2one(
        related="parent_id.survey_id", string="Questionnaire"
    )
