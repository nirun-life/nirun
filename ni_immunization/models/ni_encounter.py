#  Copyright (c) 2026 NSTDA
from odoo import fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    show_immunization = fields.Boolean(related="class_id.immunization")
    immunization_ids = fields.One2many(
        "ni.immunization", "encounter_id", string="Immunizations"
    )
    immunization_count = fields.Integer(compute="_compute_immunization_count")
    evaluation_ids = fields.One2many("ni.immunization.evaluation", "encounter_id")
    immunization_summary_ids = fields.One2many(
        related="patient_id.immunization_summary_ids", readonly=True
    )

    def _compute_immunization_count(self):
        immunization = self.env["ni.immunization"].sudo()
        read = immunization._read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["__count"]
        )
        data = {encounter.id: count for encounter, count in read}
        for enc in self:
            enc.immunization_count = data.get(enc.id, 0)

    def action_immunization_evaluation_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("Immunization Evaluation Wizard"),
            "res_model": "ni.immunization.evaluation.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_encounter_id": self.id},
        }

    def action_immunization_evaluation(self):
        return {
            "name": self.env._("Immunization Evaluation"),
            "type": "ir.actions.act_window",
            "res_model": "ni.immunization.evaluation",
            "view_mode": "list,kanban,form",
            "domain": [("patient_id", "=", self[0].patient_id.id)],
            "context": {
                "default_patient_id": self[0].patient_id.id,
                "default_encounter_id": self.ids[0],
                "search_default_group_by_disease": 1,
            },
        }

    def action_immunization(self):
        action = {
            "name": self.env._("Immunization History"),
            "type": "ir.actions.act_window",
            "res_model": "ni.immunization",
            "view_mode": "list,kanban,form",
            "context": {
                "search_default_group_by_encounter": 1,
                "default_patient_id": self[0].patient_id.id,
                "default_encounter_id": self.ids[0],
            },
            "domain": [("patient_id", "=", self[0].patient_id.id)],
        }
        return action
