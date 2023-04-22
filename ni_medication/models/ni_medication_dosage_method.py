#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class DosageMethod(models.Model):
    _name = "ni.medication.dosage.method"
    _description = "Medication Technique"
    _inherit = ["ni.coding"]
