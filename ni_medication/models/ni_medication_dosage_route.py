#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class DosageRoute(models.Model):
    _name = "ni.medication.dosage.route"
    _description = "Medication Route"
    _inherit = ["ni.coding"]
    # Route may also be use at Allergy.reaction in future

    method_id = fields.Many2one(
        "ni.medication.dosage.method", help="Default method for this route"
    )
