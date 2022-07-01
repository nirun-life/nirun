#  Copyright (c) 2021 NSTDA
from odoo import models


class QuantityUnit(models.Model):
    _name = "ni.quantity.unit"
    _description = "Unit"
    _inherit = ["coding.base"]
