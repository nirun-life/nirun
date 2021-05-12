#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    condition_ids = fields.One2many(
        "ni.condition", "patient_id", string="Condition / Problem"
    )
