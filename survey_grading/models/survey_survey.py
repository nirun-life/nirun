#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Survey(models.Model):
    _inherit = "survey.survey"

    grade_ids = fields.One2many("survey.grade", "survey_id")