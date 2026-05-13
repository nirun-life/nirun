#  Copyright (c) 2026 NSTDA
from odoo import fields, models


class EncounterClassification(models.Model):
    _inherit = "ni.encounter.class"

    immunization = fields.Boolean(default=True, help="Show/Hide Immunization")
