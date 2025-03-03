#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class SurveySubjectWizard(models.TransientModel):
    _inherit = "survey.subject.wizard"

    patient_type_id = fields.Many2one(
        "ni.patient.type", related="subject_ni_patient.type_id"
    )
    survey_id = fields.Many2one(
        domain="['|', ('target_type_ids', '=', patient_type_id), ('target_type_ids', '=', False)]"
    )
