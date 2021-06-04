#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

REQUEST_STATE_TO_ACTIVITY_STATE = {
    "active": "in-progress",
    "draft": "scheduled",
}


class ActivityGenerator(models.TransientModel):
    _name = "ni.careplan.activity.generator"
    _description = "Activity Generator"

    careplan_id = fields.Many2one("ni.careplan", required=True)
    patient_id = fields.Many2one(related="careplan_id.patient_id")
    encounter_id = fields.Many2one(related="careplan_id.encounter_id")
    service_request_ids = fields.Many2many(
        "ni.service.request", store=False, required=True
    )

    def generate_activity(self):
        activities = self.env["ni.careplan.activity"]
        for request in self.service_request_ids:
            vals = {
                "name": request.service_id.name,
                "careplan_id": self.careplan_id.id,
                "service_request_id": request.id,
                "period_start": request.period_start,
                "period_end": request.period_end,
                "state": REQUEST_STATE_TO_ACTIVITY_STATE.get(
                    request.state, "scheduled"
                ),
            }
            activities.create(vals)

        return self.careplan_id.open_activity()

    @api.constrains("service_request_ids")
    def check_service_request_ids(self):
        for rec in self:
            if not rec.service_request_ids:
                raise ValidationError(_("Please select Service Request!"))
