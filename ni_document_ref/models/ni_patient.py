#  Copyright (c) 2021-2023 NSTDA
from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    document_ids = fields.One2many("ni.document.ref", "patient_id")
