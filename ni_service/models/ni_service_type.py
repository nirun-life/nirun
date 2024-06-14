#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class ServiceType(models.Model):
    _name = "ni.service.type"
    _description = "Service Type"
    _inherit = "ni.coding"

    service_ids = fields.One2many("ni.service", "type_id")
