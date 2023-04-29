#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    medication_dispense_ids = fields.One2many(
        "ni.medication.dispense",
        "encounter_id",
        "Dispense",
    )
    medication_dispense_count = fields.Integer(compute="_compute_medication_dispense")

    @api.depends("medication_dispense_ids")
    def _compute_medication_dispense(self):
        statement = self.env["ni.medication.dispense"].sudo()
        read = statement.read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["encounter_id"]
        )
        data = {res["encounter_id"][0]: res["encounter_id_count"] for res in read}
        for enc in self:
            enc.medication_dispense_count_count = data.get(enc.id, 0)

    def action_medication_statement(self):
        action_rec = self.env.ref("ni_medication.ni_medication_statement_action")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_encounter_id": self.ids[0],
                "search_default_state_active": True,
                "search_default_state_completed": True,
                "default_patient_id": self[0].patient_id.id,
                "default_encounter_id": self.ids[0],
            }
        )
        action["context"] = ctx
        return action
