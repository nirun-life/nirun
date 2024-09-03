#  Copyright (c) 2023. NSTDA

from odoo import fields, models

from odoo.addons.ni_patient.models.ni_encounter import LOCK_STATE_DICT


class Encounter(models.Model):
    _inherit = "ni.encounter"

    communication_ids = fields.One2many(
        "ni.communication", "encounter_id", states=LOCK_STATE_DICT
    )
    communication_count = fields.Integer(compute="_compute_communication_count")

    discharge_communication_id = fields.Many2one(
        "ni.communication", domain=[("encounter_id", "=", id)]
    )
    discharge_communication_content_ids = fields.Many2many(
        related="discharge_communication_id.content_ids"
    )
    show_communication = fields.Boolean(related="class_id.communication")

    def _compute_communication_count(self):
        communication = self.env["ni.communication"].sudo()
        read = communication.read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["encounter_id"]
        )
        data = {res["encounter_id"][0]: res["encounter_id_count"] for res in read}
        for encounter in self:
            encounter.communication_count = data.get(encounter.id, 0)

    def action_communication(self):
        action_rec = self.env.ref("ni_communication.ni_communication_action").sudo()
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_group_by_encounter": 1,
                "default_patient_id": self[0].patient_id.id,
                "default_encounter_id": self.ids[0],
            }
        )
        action["context"] = ctx
        action["domain"] = [("patient_id", "=", self[0].patient_id.id)]
        return action
