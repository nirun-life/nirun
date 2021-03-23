#  Copyright (c) 2021 Piruin P.

from odoo import models


class MedicationStatementCategory(models.Model):
    _name = "ni.medication.statement.category"
    _description = "Medication Statement Category"
    _inherit = ["coding.base"]
