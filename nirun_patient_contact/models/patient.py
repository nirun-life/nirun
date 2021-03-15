#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    contact_ids = fields.One2many(
        "ni.patient.contact", "patient_id", string="Contacts", tracking=True
    )
