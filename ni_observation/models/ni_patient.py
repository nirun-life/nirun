#  Copyright (c) 2021 NSTDA

from odoo import _, fields, models


class Patient(models.Model):
    _name = "ni.patient"
    _inherit = ["ni.patient", "ni.observation.bloodgroup.mixin"]

    observation_sheet_ids = fields.One2many(
        "ni.observation.sheet",
        "patient_id",
        domain=[("active", "=", True)],
        groups="ni_observation.group_user",
    )
    observation_sheet_count = fields.Integer(compute="_compute_observation_sheet_count")
    patient_observation_ids = fields.One2many("ni.patient.observation", "patient_id")

    def _compute_observation_sheet_count(self):
        observations = self.env["ni.observation.sheet"].sudo()
        read = observations.read_group(
            [("patient_id", "in", self.ids)], ["patient_id"], ["patient_id"]
        )
        data = {res["patient_id"][0]: res["patient_id_count"] for res in read}
        for patient in self:
            patient.observation_sheet_count = data.get(patient.id, 0)

    def action_observation(self):
        action_rec = self.env.ref("ni_observation.ni_observation_action").sudo()
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

    def _name_get(self):
        name = super(Patient, self)._name_get()
        if (
            self._context.get("show_gender_age")
            and (self.age or self.gender)
            and self.blood_group
        ):
            name = _("{} • Blood group {}").format(name, self.blood_group)
        return name
