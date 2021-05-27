#  Copyright (c) 2021 Piruin P.
from odoo import fields, models


class ServiceBulkRequest(models.TransientModel):
    _name = "ni.service.request.bulk"
    _inherit = ["period.mixin"]

    service_id = fields.Many2one("ni.service", required=True)
    patient_ids = fields.Many2many(
        "ni.patient",
        string="Patient(s)",
        required=True,
        domain=[("encountering_id", "!=", False)],
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
                    "encounter_id": patient.encountering_id.id,
                    "service_id": self.service_id.id,
                    "requester_id": self.env.user.partner_id.id,
                    "period_start": self.period_start,
                    "period_end": self.period_end,
                }
            )
        return self.service_id.open_request()