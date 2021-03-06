#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    religion = fields.Many2one(
        "res.religion", string="Religion", tracking=True, require=False
    )
