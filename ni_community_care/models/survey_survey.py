#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class Survey(models.Model):
    _inherit = "survey.survey"

    target_type_ids = target_type_ids = fields.Many2many(
        "ni.patient.type",
        "survey_survey_target_type",
        "survey_id",
        "type_id",
        "กลุ่มเป้าหมาย",
    )
    category_id = fields.Many2one("ni.observation.category")
