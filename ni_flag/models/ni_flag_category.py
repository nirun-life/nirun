#  Copyright (c) 2026 NSTDA
from odoo import models


class FlagCategory(models.Model):
    _name = "ni.flag.category"
    _description = "Flag Category"
    _inherit = ["ni.coding"]
