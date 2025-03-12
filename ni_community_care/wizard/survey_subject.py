#  Copyright (c) 2021 NSTDA


from odoo import api, fields, models


class SurveySubjectWizard(models.TransientModel):
    _inherit = "survey.subject.wizard"

    category_id = fields.Many2one(
        "ni.observation.category",
        "มิติ",
        domain="[('type_count', '>', 0)]",
    )
    survey_id = fields.Many2one(
        domain="['|', ('category_id', '=', category_id), ('category_id', '=', False)]"
    )

    @api.onchange("category_id")
    def _onchange_category_id(self):
        for rec in self:
            if rec.survey_id and rec.survey_id.category_id != rec.category_id:
                rec.survey_id = None
