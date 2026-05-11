#  Copyright (c) 2026 NSTDA
from odoo import _, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    immunization_ids = fields.One2many("ni.immunization", "patient_id", readonly=True)
    immunization_count = fields.Integer(compute="_compute_immunization_count")

    evaluation_ids = fields.One2many(
        "ni.immunization.evaluation", "patient_id", readonly=True
    )
    immunization_summary_ids = fields.One2many(
        "ni.immunization.summary", "patient_id", readonly=True
    )
    protected_disease_count = fields.Integer(compute="_compute_protected_disease_count")

    def _compute_immunization_count(self):
        immunization = self.env["ni.immunization"].sudo()
        read = immunization.read_group(
            [("patient_id", "in", self.ids)], ["patient_id"], ["patient_id"]
        )
        data = {res["patient_id"][0]: res["patient_id_count"] for res in read}
        for patient in self:
            patient.immunization_count = data.get(patient.id, 0)

    def _compute_protected_disease_count(self):
        evaluation = self.env["ni.immunization.evaluation"].sudo()
        for patient in self:
            diseases = evaluation.search(
                [
                    ("patient_id", "=", patient.id),
                    ("protection_status", "=", "protected"),
                ]
            ).mapped("target_disease_id")
            patient.protected_disease_count = len(diseases)

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

    def action_immunization_evaluation(self):
        return {
            "name": _("Immunization Protection"),
            "type": "ir.actions.act_window",
            "res_model": "ni.immunization.evaluation",
            "view_mode": "kanban,tree,form",
            "domain": [("patient_id", "=", self.ids[0])],
            "context": {
                "default_patient_id": self.ids[0],
                "search_default_group_by_disease": 1,
            },
        }
