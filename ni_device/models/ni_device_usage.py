#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class DeviceUsage(models.Model):
    _name = "ni.device.usage"
    _inherit = ["ni.patient.res", "ni.workflow.event"]
    _description = "Device Usage"

    device_id = fields.Many2one(
        "ni.device", required=True, index=True, ondelete="cascade"
    )

    state = fields.Selection(
        [
            ("in-progress", "Active"),
            ("suspended", "On Hold"),
            ("abort", "Stopped"),
            ("completed", "Completed"),
        ],
        "State",
        required=True,
        default="in-progress",
    )
