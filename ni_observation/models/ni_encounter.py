#  Copyright (c) 2021-2023. NSTDA

from odoo import api, fields, models

OBSERVATION_FIELDS = [
    "bp_s",
    "bp_d",
    "heart_rate",
    "respiratory_rate",
    "body_temp",
    "body_weight",
    "body_height",
    "bmi",
    "fbs",
]


class Encounter(models.Model):
    _inherit = "ni.encounter"

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

    bp = fields.Char("Blood Pressure")
    bp_s = fields.Float("SYS")
    bp_d = fields.Float("DIA")
    heart_rate = fields.Integer("Heart Rate (Pulse)")
    respiratory_rate = fields.Integer("Respiratory Rate")
    body_temp = fields.Float("Body Temperature")
    body_weight = fields.Float("Body Weight")
    body_height = fields.Float("Body Height")
    bmi = fields.Float("Body Mass Index", compute="_compute_bmi", store=True)
    fbs = fields.Float("Fasting Blood Sugar")

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
        for f in OBSERVATION_FIELDS:
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
            "encounter_id": self.encounter_id.id,
            "type_id": type_id,
            "value": value,
        }

    @api.depends("body_height", "body_weight")
    def _compute_bmi(self):
        for rec in self:
            if rec.body_height and rec.body_weight:
                body_height_m = rec.body_height * 0.01
                rec.bmi = rec.body_weight / pow(body_height_m, 2)
            else:
                rec.bmi = 0.0

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
        action_rec = self.env.ref("ni_observation.ni_observation_action")
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
