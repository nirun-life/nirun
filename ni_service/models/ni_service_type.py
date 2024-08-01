#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class ServiceType(models.Model):
    _name = "ni.service.type"
    _description = "Service Type"
    _inherit = "ni.coding"

    service_ids = fields.One2many("ni.service", "type_id")
    decoration = fields.Selection(
        [
            ("primary", "Primary"),
            ("success", "Success"),
            ("info", "Info"),
            ("warning", "Warning"),
            ("danger", "Danger"),
            ("muted", "Muted"),
        ],
        default="muted",
        required=True,
    )
