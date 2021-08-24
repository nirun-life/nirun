#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    condition_ids = fields.One2many(
        "ni.condition", "encounter_id", string="Encounter Diagnosis", check_company=True
    )
