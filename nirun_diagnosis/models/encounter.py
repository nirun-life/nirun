#  Copyright (c) 2023-2023. NSTDA

from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    diagnosis_ids = fields.One2many("ni.encounter.diagnosis", "encounter_id")
