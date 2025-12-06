#  Copyright (c) 2025 NSTDA
from odoo import models


class DeviceDisposeType(models.Model):
    _name = "ni.device.dispose.type"
    _description = "Device Dispose Type"
    _inherit = ["ni.coding"]
