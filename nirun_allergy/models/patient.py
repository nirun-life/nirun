#  Copyright (c) 2021 NSTDA
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Patient(models.Model):
    _inherit = "ni.patient"

    allergy_ids = fields.One2many("ni.allergy", "patient_id", check_company=True)
    no_allergy = fields.Boolean()

    @api.constrains("allergy_ids", "no_allergy")
    def _check_no_allergy(self):
        for rec in self:
            if rec.no_allergy and rec.allergy_ids:
                raise ValidationError(_("Allergies and No Allergy conflict!"))
