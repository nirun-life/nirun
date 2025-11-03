#  Copyright (c) 2025 NSTDA
from odoo import models


class ReletiveBenefit(models.Model):
    _name = "ni.relative.benefit"
    _description = "Reletive Benefit"
    _inherit = ["ni.benefit"]
