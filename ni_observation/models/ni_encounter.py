#  Copyright (c) 2021-2023. NSTDA

from odoo import api, fields, models

from .ni_observation_vitalsign_mixin import VITALSIGN_FIELDS


class Encounter(models.Model):
    _name = "ni.encounter"
    _inherit = ["ni.encounter", "ni.observation.vitalsign.mixin"]

    observation_sheet_ids = fields.One2many(
        "ni.observation.sheet",
        "encounter_id",
        domain=[("active", "=", True)],
        groups="ni_observation.group_user",
    )
    observation_sheet_count = fields.Integer(compute="_compute_observation_sheet_count")
    observation_ids = fields.One2many("ni.observation", "encounter_id")
    observation_latest_ids = fields.One2many("ni.encounter.observation", "encounter_id")
    observation_line_vital_sign_ids = fields.One2many(
        "ni.encounter.observation",
        "encounter_id",
        compute="_compute_observation_line_vital_sign_ids",
    )
    observation_lab_ids = fields.One2many(
        "ni.encounter.observation",
        "encounter_id",
        compute="_compute_observation_lab_ids",
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(Encounter, self).create(vals_list)
        for rec, vals in zip(res, vals_list):
            rec._create_observation(vals)
        return res

    def write(self, vals):
        res = super(Encounter, self).write(vals)
        for rec in self:
            rec._create_observation(vals)
        return res

    def _create_observation(self, vals):
        ts = fields.Datetime.now()
        vals_list = []
        types = self.env["ni.observation.type"]
        for f in VITALSIGN_FIELDS:
            if f in vals and vals[f]:
                ob_type = types.search([("code", "=", f.replace("_", "-"))])
                value = vals[f]
                if type(value) is float:
                    value = round(value, 2)
                vals_list.append(self._observation_vals(ts, ob_type.id, value))
        if ("body_height" in vals or "body_weight" in vals) and self.bmi:
            # write BMI if any change
            bmi_type = types.search([("code", "=", "bmi")])
            vals_list.append(
                self._observation_vals(ts, bmi_type.id, round(self.bmi, 2))
            )
        if vals_list:
            return self.env["ni.observation"].create(vals_list)

    def _observation_vals(self, occurrence, type_id, value):
        return {
            "occurrence": occurrence,
            "patient_id": self.patient_id.id,
            "encounter_id": self.id,
            "type_id": type_id,
            "value": value,
        }

    def _compute_observation_sheet_count(self):
        observations = self.env["ni.observation.sheet"].sudo()
        read = observations.read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["encounter_id"]
        )
        data = {res["encounter_id"][0]: res["encounter_id_count"] for res in read}
        for encounter in self:
            encounter.observation_sheet_count = data.get(encounter.id, 0)

    @api.depends("observation_latest_ids")
    def _compute_observation_line_vital_sign_ids(self):
        ob_lines = self.env["ni.encounter.observation"].search(
            [("encounter_id", "in", self.ids), ("category_id.code", "=", "vital-signs")]
        )
        for rec in self:
            rec.observation_line_vital_sign_ids = ob_lines.filtered_domain(
                [("encounter_id", "=", rec.id)]
            )

    @api.depends("observation_latest_ids")
    def _compute_observation_lab_ids(self):
        ob_lines = self.env["ni.encounter.observation"].search(
            [("encounter_id", "in", self.ids), ("category_id.code", "=", "laboratory")]
        )
        for rec in self:
            rec.observation_lab_ids = ob_lines.filtered_domain(
                [("encounter_id", "=", rec.id)]
            )

    def action_observation(self):
        action_rec = self.env.ref("ni_observation.ni_observation_action").sudo()
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "default_patient_id": self[0].patient_id.id,
                "default_encounter_id": self.ids[0],
            }
        )
        domain = [
            ("patient_id", "=", self.patient_id.id),
            ("encounter_id", "<=", self.id),
        ]
        if "category_id" in ctx and ctx["category_id"]:
            domain.append(("category_id", "=", ctx["category_id"]))

        action["context"] = ctx
        action["domain"] = domain
        return action
