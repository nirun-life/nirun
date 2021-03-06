#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    observation_ids = fields.One2many(
        "ni.observation", "patient_id", domain=[("active", "=", True)]
    )
    observation_count = fields.Integer(compute="_compute_observation_count")

    @api.depends("observation_ids")
    def _compute_observation_count(self):
        for rec in self:
            rec.observation_count = len(rec.observation_ids)

    def action_observation(self):
        action_rec = self.env.ref("nirun_observation.ob_action")
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
