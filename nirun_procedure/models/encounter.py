#  Copyright (c) 2022. NSTDA

from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    procedure_ids = fields.One2many(
        "ni.procedure",
        "encounter_id",
    )
    procedure_count = fields.Integer(compute="_compute_procedure_count")

    def _compute_procedure_count(self):
        procedure = self.env["ni.procedure"].sudo()
        read = procedure.read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["encounter_id"]
        )
        data = {res["encounter_id"][0]: res["encounter_id_count"] for res in read}
        for encounter in self:
            encounter.procedure_count = data.get(encounter.id, 0)

    def action_procedure(self):
        action_rec = self.env.ref("nirun_procedure.procedure_action")
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