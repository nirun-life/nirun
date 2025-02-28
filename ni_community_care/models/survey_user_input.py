#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class SurveyGrade(models.Model):
    _inherit = "survey.grade"

    patient_type_id = fields.Many2one("ni.patient.type")


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    def _onchange_state_done(self):
        super()._onchange_state_done()
        for rec in self:
            if rec.grade_id.patient_type_id:
                subject = self.env[rec.survey_id.subject_type].browse(rec.subject_id)
                subject.write({"type_id": rec.grade_id.patient_type_id.id})
