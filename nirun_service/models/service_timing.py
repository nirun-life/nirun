#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class HealthcareServiceTiming(models.Model):
    _name = "ni.service.timing"
    _description = "Healthcare Service Event Timing"
    _inherits = {"ni.timing": "timing_id"}
    _inherit = "ni.timing.mixin"

    service_id = fields.Many2one("ni.service", required=True, ondelete="cascade")
    timing_id = fields.Many2one(required=True, ondelete="cascade")
