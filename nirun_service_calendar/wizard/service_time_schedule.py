#  Copyright (c) 2021 NSTDA

from odoo import api, fields, models


class HealthcareServiceTimingCalendarWizard(models.TransientModel):
    _name = "ni.service.time.schedule"
    _description = "Healthcare Service Schedule"
    _inherit = ["period.mixin"]

    service_id = fields.Many2one("ni.service", required=True)
    time_id = fields.Many2one(
        "ni.service.time", domain="[('service_id', '=', service_id)]"
    )
    timing_id = fields.Many2one(
        "ni.service.timing", domain="[('service_id', '=', service_id)]"
    )
    partner_ids = fields.Many2many(
        "res.partner",
        string="Participant",
        compute="_compute_partner_ids",
        readonly=False,
    )
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)

    @api.onchange("period_start")
    def onchange_period_start(self):
        if not self.period_end or self.period_end < self.period_start:
            self.period_end = self.period_start

    @api.depends("period_start", "period_end")
    def _compute_partner_ids(self):
        # FIXME remove participant from event that not on their request period
        for rec in self:
            request = self.env["ni.service.request"].get_intercept_period(
                rec.period_start,
                rec.period_end,
                domain=[
                    ("service_id", "=", rec.service_id.id),
                    ("state", "in", ["active"]),
                ],
            )
            rec.partner_ids = [
                (6, 0, request.mapped("partner_id").ids if request else [])
            ]

    def schedule(self):
        val = self._get_calendar_dict()
        time = self.time_id or self.timing_id
        val.update(time.get_calendar_dict(self.period_start))
        # if self.time_id:
        #     val.update(self.get_calendar_dict(self.period_start))
        # elif self.timing_id:
        #     val.update(self.timing_id.get_calendar_dict(self.period_start))
        events = self.env["calendar.event"]
        events.create(val)

        return self.service_id.action_calendar_event()

    def _get_calendar_dict(self):
        self.ensure_one()
        return {
            "res_id": self.service_id.id,
            "res_model": "ni.service",
            "recurrency": True,
            "end_type": "end_date",
            "final_date": self.period_end,
            "name": self.service_id.name,
            "location": self.service_id.location,
            "partner_ids": self.partner_ids,
            "attendee_ids": [
                (
                    0,
                    0,
                    {
                        "state": "tentative",
                        "partner_id": partner.id,
                        "email": partner.email,
                        "availability": "busy",
                    },
                )
                for partner in self.partner_ids
            ],
        }
