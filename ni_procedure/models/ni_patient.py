#  Copyright (c) 2022. NSTDA

from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    procedure_ids = fields.One2many("ni.procedure", "patient_id", readonly=True)
    procedure_count = fields.Integer(compute="_compute_procedure_count")

    def _compute_procedure_count(self):
        procedures = self.env["ni.procedure"].sudo()
        read = procedures.read_group(
            [("patient_id", "in", self.ids)], ["patient_id"], ["patient_id"]
        )
        data = {res["patient_id"][0]: res["patient_id_count"] for res in read}
        for patient in self:
            patient.procedure_count = data.get(patient.id, 0)

    def action_procedure(self):
        action_rec = self.env.ref("ni_procedure.ni_procedure_action").sudo()
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
