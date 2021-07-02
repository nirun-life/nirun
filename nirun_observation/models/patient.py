#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    observation_ids = fields.One2many(
        "ni.observation",
        "patient_id",
        domain=[("active", "=", True)],
        groups="nirun_observation.group_user",
    )
    observation_count = fields.Integer(compute="_compute_observation_count")

    def _compute_observation_count(self):
        observations = self.env["ni.observation"].sudo()
        read = observations.read_group(
            [("patient_id", "in", self.ids)], ["patient_id"], ["patient_id"]
        )
        data = {res["patient_id"][0]: res["patient_id_count"] for res in read}
        for patient in self:
            patient.observation_count = data.get(patient.id, 0)

    def action_observation(self):
        action_rec = self.env.ref("nirun_observation.ob_action")
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
