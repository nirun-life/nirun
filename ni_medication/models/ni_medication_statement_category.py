#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class MedicationStatementCategory(models.Model):
    _name = "ni.medication.statement.category"
    _description = "Medication Statement Category"
    _inherit = ["ni.coding"]
