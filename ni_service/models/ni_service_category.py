#  Copyright (c) 2024 NSTDA
from odoo import models


class ServiceCategory(models.Model):
    _name = "ni.service.category"
    _description = "Service Category"
    _inherit = "ni.coding"
