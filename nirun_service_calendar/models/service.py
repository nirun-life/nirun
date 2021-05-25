#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class HealthcareService(models.Model):
    _inherit = "ni.service"

    event_ids = fields.One2many("calendar.event", "service_id")
    event_count = fields.Integer(compute="_compute_event")
    location = fields.Char(compute="_compute_location")

    @api.depends("event_ids")
    def _compute_event(self):
        for rec in self:
            rec.event_count = len(rec.event_ids)

    @api.depends("location_ids")
    def _compute_location(self):
        for rec in self:
            rec.location = ", ".join(rec.location_ids.mapped("name"))

    def action_calendar_event(self):
        action_rec = self.env.ref("calendar.action_calendar_event")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        service = self[0]
        ctx.update(
            {
                "search_default_service_id": service.id,
                "default_name": service.name,
                "default_service_id": service.id,
            }
        )
        action["context"] = ctx
        return action
