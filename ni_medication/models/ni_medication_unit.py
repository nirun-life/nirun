#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class MedicationForm(models.Model):
    _name = "ni.medication.unit"
    _description = "Medication Unit"
    _inherit = ["ni.coding"]
