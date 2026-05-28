#  Copyright (c) 2024 NSTDA


from odoo import api, fields, models


class SurveySubjectWizard(models.TransientModel):
    _inherit = "survey.subject.wizard"

    patient_type_id = fields.Many2one(
        "ni.patient.type", related="subject_ni_patient.type_id"
    )
    patient_type_decoration = fields.Selection(
        related="subject_ni_patient.type_id.decoration"
    )
    category_id = fields.Many2one(
        "ni.observation.category",
        "มิติ",
        domain="[('type_count', '>', 0)]",
    )
    survey_id = fields.Many2one(
        domain="['&',"
        " '|', ('target_type_ids', '=', patient_type_id), ('target_type_ids', '=', False),"
        " '|', ('category_id', '=', category_id), ('category_id', '=', False)]"
    )

    @api.onchange("category_id")
    def _onchange_category_id(self):
        for rec in self:
            if rec.survey_id and rec.survey_id.category_id != rec.category_id:
                rec.survey_id = None
