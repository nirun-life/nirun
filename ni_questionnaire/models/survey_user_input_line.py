#  Copyright (c) 2021-2023. NSTDA

from odoo import fields, models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input.line"

    company_id = fields.Many2one(
        "res.company", related="user_input_id.company_id", required=False, store=True
    )
