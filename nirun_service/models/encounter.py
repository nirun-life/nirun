#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    service_request_ids = fields.One2many(
        "ni.service.request",
        "encounter_id",
        "Service Requests",
        check_company=True,
        groups="nirun_service.group_user",
    )
    service_request_count = fields.Integer(
        "Services", compute="_compute_service_request_count", sudo_compute=True
    )

    def _compute_service_request_count(self):
        count = self._count_active_service_request()
        for rec in self:
            rec.service_request_count = count.get(rec.id)

    def _count_active_service_request(self):
        domain = [("encounter_id", "in", self.ids), ("state", "=", "active")]
        read = (
            self.env["ni.service.request"]
            .sudo()
            .read_group(domain, ["encounter_id"], ["encounter_id"],)
        )
        return {data["encounter_id"][0]: data["encounter_id_count"] for data in read}

    def open_service_request(self):
        self.ensure_one()
        enc = self
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_group_by_intent": True,
                "default_patient_id": enc.patient_id.id,
                "default_encounter_id": enc.id,
            }
        )
        action = self.env["ir.actions.act_window"].for_xml_id(
            "nirun_service", "service_request_action"
        )
        return dict(action, context=ctx, domain=[("encounter_id", "=", enc.id)])
