#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class SurveyGrade(models.Model):
    _inherit = "survey.grade"

    patient_group_id = fields.Many2one("ni.patient.group")