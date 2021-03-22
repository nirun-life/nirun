#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.encounter"

    medication_ids = fields.One2many(
        "ni.medication.statement",
        "encounter_id",
        string="Medication Statements",
        domain=[("state", "in", ["active", "completed"])],
    )
    medication_count = fields.Integer(compute="_compute_medication_count")

    @api.depends("medication_ids")
    def _compute_medication_count(self):
        for rec in self:
            rec.medication_count = len(rec.medication_ids)

    def action_medication_statement(self):
        action_rec = self.env.ref("nirun_medication.medication_statement_action")
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
