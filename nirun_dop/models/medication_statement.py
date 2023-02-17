#  Copyright (c) 2023. NSTDA

from odoo import fields, models


class MedicationStatement(models.Model):
    _inherit = "ni.medication.statement"

    dispense_partner_id = fields.Many2one(
        "res.partner", domain="[('is_company', '=', True)]"
    )
