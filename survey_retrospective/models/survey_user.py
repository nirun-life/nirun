#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    retrospective = fields.Boolean()
