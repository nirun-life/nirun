#  Copyright (c) 2025 NSTDA
from odoo import models


class DeviceType(models.Model):
    _name = "ni.device.type"
    _description = "Device Type"
    _inherit = ["ni.coding"]
