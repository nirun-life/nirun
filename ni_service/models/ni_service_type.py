#  Copyright (c) 2024 NSTDA
from odoo import models


class ServiceType(models.Model):
    _name = "ni.service.type"
    _description = "Service Type"
    _inherit = "ni.coding"
