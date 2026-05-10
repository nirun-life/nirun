#  Copyright (c) 2026 NSTDA
from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    immunization_ids = fields.One2many("ni.immunization", "patient_id", readonly=True)
    immunization_count = fields.Integer(compute="_compute_immunization_count")

    def _compute_immunization_count(self):
        immunization = self.env["ni.immunization"].sudo()
        read = immunization.read_group(
            [("patient_id", "in", self.ids)], ["patient_id"], ["patient_id"]
        )
        data = {res["patient_id"][0]: res["patient_id_count"] for res in read}
        for patient in self:
            patient.immunization_count = data.get(patient.id, 0)

    def action_immunization(self):
        action_rec = self.env.ref("ni_immunization.ni_immunization_action").sudo()
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_patient_id": self.ids[0],
                "default_patient_id": self.ids[0],
            }
        )
        action["context"] = ctx
        return action
