#  Copyright (c) 2021 Piruin P.

from odoo import models


class MedicationForm(models.Model):
    _name = "ni.medication.form"
    _description = "Medication Form"
    _inherit = ["coding.base"]
