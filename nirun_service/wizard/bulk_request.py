#  Copyright (c) 2021 NSTDA
from odoo import fields, models


class ServiceBulkRequest(models.TransientModel):
    _name = "ni.service.request.bulk"
    _description = "Service Request(s)"
    _inherit = ["period.mixin"]

    service_id = fields.Many2one("ni.service", required=True)
    patient_ids = fields.Many2many(
        "ni.patient",
        string="Patients",
        required=True,
        domain=[("encounter_id", "!=", False)],
    )
    service_available_type = fields.Selection(related="service_id.available_type")
    service_available_timing_ids = fields.One2many(
        related="service_id.available_timing_ids",
    )
    service_timing_id = fields.Many2one(
        "ni.service.timing",
        string="Event",
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="[('id', 'in', service_available_timing_ids)]",
        help="When service should occur",
    )
    service_available_time_ids = fields.One2many(
        related="service_id.available_time_ids"
    )
    service_time_id = fields.Many2one(
        "ni.service.time",
        string="Routine",
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="[('id', 'in', service_available_time_ids)]",
        help="What routine this request will participant",
    )
    state = fields.Selection(
        [("draft", "Request"), ("active", "In-Progress")],
        required=True,
        default="draft",
    )

    def create_bulk_request(self):
        req = self.env["ni.service.request"]
        for patient in self.patient_ids:
            req.create(
                {
                    "patient_id": patient.id,
                    "encounter_id": patient.encounter_id.id,
                    "service_id": self.service_id.id,
                    "requester_id": self.env.user.partner_id.id,
                    "period_start": self.period_start,
                    "period_end": self.period_end,
                    "state": self.state,
                    "service_time_id": self.service_time_id.id
                    if self.service_available_type == "routine"
                    else False,
                    "service_timing_id": self.service_timing_id.id
                    if self.service_available_type == "event"
                    else False,
                }
            )
        return self.service_id.open_request(self.state)
