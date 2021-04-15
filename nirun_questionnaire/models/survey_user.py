#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    patient_id = fields.Many2one(
        "ni.patient",
        required=False,
        index=True,
        domain="[('company_id', '=', lambda self: self.env.company)]",
    )
    encounter_id = fields.Many2one(
        "ni.encounter",
        index=True,
        required=False,
        domain="[('patient_id', '=', patient_id)]",
    )

    @api.constrains("encounter_id")
    def check_encounter_id(self):
        for rec in self:
            if not rec.encounter_id:
                continue
            if rec.patient_id != rec.encounter_id.patient_id:
                raise ValidationError(
                    _("The referencing encounter is not belong to patient")
                )
