#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    service_request_ids = fields.One2many(
        "ni.service.request", "patient_id", "Service Requests",
    )
    service_request_count = fields.Integer(
        "Services", compute="_compute_service_request_count", sudo_compute=True
    )

    @api.depends("service_request_ids", "service_request_ids.state")
    def _compute_service_request_count(self):
        count = self._count_active_service_request()
        for rec in self:
            rec.service_request_count = count.get(rec.id)

    def _count_active_service_request(self):
        _domain = [("patient_id", "in", self.ids), ("state", "=", "active")]
        req = self.env["ni.service.request"].read_group(
            _domain, ["patient_id"], ["patient_id"],
        )
        return {data["patient_id"][0]: data["patient_id_count"] for data in req}

    def open_service_request(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.ids[0],
                "search_default_active": True,
                "default_patient_id": self.ids[0],
            }
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_service", "service_request_action"
        )
        return dict(action, context=ctx)
