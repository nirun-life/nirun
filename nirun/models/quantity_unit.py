#  Copyright (c) 2021 Piruin P.
from odoo import models


class QuantityUnit(models.Model):
    _name = "ni.quantity.unit"
    _description = "Unit"
    _inherit = ["coding.base"]
