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
                }
            )
        return self.service_id.open_request(self.state)
