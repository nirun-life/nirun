#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class ObservationReport(models.AbstractModel):
    _inherit = "ni.observation.report"

    device_id = fields.Many2one("ni.device", readonly=True)
