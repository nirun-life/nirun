#  Copyright (c) 2021-2023. NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    observation_sheet_ids = fields.One2many(
        "ni.observation.sheet",
        "encounter_id",
        domain=[("active", "=", True)],
        groups="ni_observation.group_user",
    )
    observation_sheet_count = fields.Integer(compute="_compute_observation_sheet_count")

    observation_ids = fields.One2many("ni.encounter.observation", "encounter_id")
    observation_line_vital_sign_ids = fields.One2many(
        "ni.encounter.observation",
        "encounter_id",
        compute="_compute_observation_line_vital_sign_ids",
    )

    def _compute_observation_sheet_count(self):
        observations = self.env["ni.observation.sheet"].sudo()
        read = observations.read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["encounter_id"]
        )
        data = {res["encounter_id"][0]: res["encounter_id_count"] for res in read}
        for encounter in self:
            encounter.observation_sheet_count = data.get(encounter.id, 0)

    @api.depends("observation_ids")
    def _compute_observation_line_vital_sign_ids(self):
        ob_lines = self.env["ni.encounter.observation"].search(
            [("encounter_id", "in", self.ids), ("category_id.code", "=", "vital-signs")]
        )
        for rec in self:
            rec.observation_line_vital_sign_ids = ob_lines.filtered_domain(
                [("encounter_id", "=", rec.id)]
            )

    def action_observation(self):
        self.ensure_one()
        action_rec = self.env.ref("ni_observation.ni_observation_action")
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_patient_id": self[0].patient_id.id,
                "default_encounter_id": self.ids[0],
            }
        )
        action["context"] = ctx
        action["domain"] = [("encounter_id", "=", self.id)]
        return action
