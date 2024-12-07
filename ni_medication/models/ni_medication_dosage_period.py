#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class DosagePeriod(models.Model):
    _name = "ni.medication.dosage.period"
    _description = "Medication Dosage Period"
    _inherit = ["ni.coding"]
