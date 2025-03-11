#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class DosagePeriod(models.Model):
    _name = "ni.medication.dosage.period_meal"
    _description = "Medication Dosage Meal"
    _inherit = ["ni.coding"]
