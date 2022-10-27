#  Copyright (c) 2022. NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    immunization_ids = fields.One2many("ni.immunization", "encounter_id")
    immunization_count = fields.Integer(compute="_compute_immunization")

    @api.depends("immunization_ids")
    def _compute_immunization(self):
        immunization = self.env["ni.immunization"].sudo()
        read = immunization.read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["encounter_id"]
        )
        data = {res["encounter_id"][0]: res["encounter_id_count"] for res in read}
        for enc in self:
            enc.immunization_count = data.get(enc.id, 0)

    def action_immunization(self):
        action_rec = self.env.ref("nirun_immunization.immunization_action")
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
