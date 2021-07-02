#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    observation_ids = fields.One2many(
        "ni.observation",
        "encounter_id",
        domain=[("active", "=", True)],
        groups="nirun_observation.group_user",
    )
    observation_count = fields.Integer(compute="_compute_observation_count")

    def _compute_observation_count(self):
        observations = self.env["ni.observation"].sudo()
        read = observations.read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["encounter_id"]
        )
        data = {res["encounter_id"][0]: res["encounter_id_count"] for res in read}
        for encounter in self:
            encounter.observation_count = data.get(encounter.id, 0)

    def action_observation(self):
        action_rec = self.env.ref("nirun_observation.ob_action")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_encounter_id": self.ids[0],
                "default_patient_id": self[0].patient_id.id,
                "default_encounter_id": self.ids[0],
            }
        )
        action["context"] = ctx
        return action
