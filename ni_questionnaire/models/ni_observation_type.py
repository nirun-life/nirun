#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class ObservationType(models.Model):
    _inherit = "ni.observation.type"

    survey_id = fields.Many2one("survey.survey")
