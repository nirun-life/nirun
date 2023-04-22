#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class MedicationForm(models.Model):
    _name = "ni.medication.form"
    _description = "Medication Form"
    _inherit = ["ni.coding"]
