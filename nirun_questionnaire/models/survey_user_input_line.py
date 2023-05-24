#  Copyright (c) 2021-2023. NSTDA

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class SurveyUserInputLLine(models.Model):
    _inherit = "survey.user_input_line"

    company_id = fields.Many2one(related='user_input_id.company_id')

