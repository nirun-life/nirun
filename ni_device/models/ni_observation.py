#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class Observation(models.Model):
    _inherit = "ni.observation"

    device_id = fields.Many2one("ni.device", index=True)
