#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class HealthcareServiceTiming(models.Model):
    _name = "ni.service.timing"
    _description = "Healthcare Service Event Timing"
    _inherit = ["ni.timing"]

    service_id = fields.Many2one("ni.service", ondelete="cascade")

    day_of_week = fields.Many2many(
        "ni.timing.dow", "ni_service_timing_dow", "timing_id", "dow_id"
    )
    when = fields.Many2many(
        "ni.timing.event",
        "ni_service_timing_event",
        "timing_id",
        "event_id",
        auto_join=True,
    )
