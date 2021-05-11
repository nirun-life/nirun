#  Copyright (c) 2021 Piruin P.
from odoo import fields, models


class Admission(models.TransientModel):
    _name = "ni.patient.admission"
    _description = "Admission"

    encounter_id = fields.Many2one("ni.encounter")
