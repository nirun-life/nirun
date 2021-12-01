#  Copyright (c) 2021 Piruin P.

from odoo import models


class DosageMethod(models.Model):
    _name = "ni.medication.dosage.method"
    _description = "Medication Technique"
    _inherit = ["coding.base"]
