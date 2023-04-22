#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class DosageRoute(models.Model):
    _name = "ni.medication.dosage.route"
    _description = "Medication Route"
    _inherit = ["ni.coding"]
    # Route may also be use at Allergy.reaction in future
