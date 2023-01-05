#  Copyright (c) 2022. NSTDA

from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    document_ids = fields.One2many("ni.document", "encounter_id")
