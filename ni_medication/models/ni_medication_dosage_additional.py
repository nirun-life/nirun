#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class DosageAdditionalInstruction(models.Model):
    _name = "ni.medication.dosage.additional"
    _description = "Dosage Additional Instruction"
    _inherit = ["ni.coding"]
