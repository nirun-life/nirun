#  Copyright (c) 2021 Piruin P.
from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    contact_ids = fields.One2many(related="partner_id.child_ids", readonly=False)
