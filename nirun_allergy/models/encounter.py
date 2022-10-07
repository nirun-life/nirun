#  Copyright (c) 2022. NSTDA

from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    allergy_ids = fields.One2many(related="patient_id.allergy_ids", readonly=False)
    no_allergy = fields.Boolean(related="patient_id.no_allergy", readonly=False)
