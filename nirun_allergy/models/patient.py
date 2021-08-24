#  Copyright (c) 2021 Piruin P.
from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    allergy_ids = fields.One2many("ni.allergy", "patient_id", check_company=True)
