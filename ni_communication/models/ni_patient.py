#  Copyright (c) 2023. NSTDA

from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    communication_ids = fields.One2many("ni.communication", "patient_id", readonly=True)
    communication_count = fields.Integer(compute="_compute_communication_count")

    def _compute_communication_count(self):
        communications = self.env["ni.communication"].sudo()
        read = communications._read_group(
            [("patient_id", "in", self.ids)], ["patient_id"], ["__count"]
        )
        data = {patient.id: count for patient, count in read}
        for patient in self:
            patient.communication_count = data.get(patient.id, 0)

    def action_communication(self):
        action_rec = self.env.ref("ni_communication.ni_communication_action").sudo()
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
