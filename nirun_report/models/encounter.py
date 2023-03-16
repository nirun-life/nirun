#  Copyright (c) 2022 Piruin P.

from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    gender = fields.Selection(related="patient_id.gender", store=True)
