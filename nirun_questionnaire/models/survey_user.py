#  Copyright (c) 2021 Piruin P.

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SurveyUserInput(models.Model):
    _name = "survey.user_input"
    _inherit = ["survey.user_input", "ni.patient.res"]

    @api.constrains("encounter_id")
    def check_encounter_id(self):
        for rec in self:
            if rec.encounter_id and rec.patient_id != rec.encounter_id.patient_id:
                raise ValidationError(
                    _("The referencing encounter is not belong to patient")
                )
