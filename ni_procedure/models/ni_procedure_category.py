#  Copyright (c) 2022. NSTDA
from odoo import models


class ProcedureCategory(models.Model):
    _name = "ni.procedure.category"
    _description = "Procedure Category"
    _inherit = ["ni.coding"]
