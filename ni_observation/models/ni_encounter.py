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
    observation_category_id = fields.Many2one(
        "ni.observation.category",
        default=lambda self: self.env.ref("ni_observation.category_vital_signs").id,
        domain=[("type_count", ">", 0)],
    )
    observation_problem_only = fields.Boolean(
        default=False,
        store=False,
        help="Check here to display only the problem observations",
    )
    encounter_observation_ids = fields.One2many(
        "ni.encounter.observation", "encounter_id"
    )
    filtered_encounter_observation_ids = fields.One2many(
        "ni.encounter.observation", compute="_compute_display_observation"
    )
    filtered_patient_observation_ids = fields.One2many(
        "ni.patient.observation", compute="_compute_display_observation"
    )

    observation_filter = fields.Selection(
        [
            ("encounter", "This Encounter"),
            ("patient", "All"),
        ],
        default="encounter",
        require=True,
    )

    observation_latest_ids = fields.One2many("ni.encounter.observation", "encounter_id")
    observation_latest_count = fields.Integer(
        compute="_compute_observation_latest",
    )
    observation_latest_vital_sign_ids = fields.One2many(
        "ni.encounter.observation",
        "encounter_id",
        compute="_compute_observation_latest",
    )
    observation_latest_vital_sign_count = fields.Integer(
        compute="_compute_observation_latest",
    )
    observation_latest_lab_ids = fields.One2many(
        "ni.encounter.observation",
        "encounter_id",
        compute="_compute_observation_latest",
    )
    observation_latest_lab_count = fields.Integer(compute="_compute_observation_latest")

    @api.depends(
        "observation_category_id", "observation_filter", "observation_problem_only"
    )
    def _compute_display_observation(self):
        for rec in self:
            domain = [("category_id", "=", rec.observation_category_id.id)]
            if rec.observation_problem_only:
                domain += [("is_problem", "=", True)]
            if rec.observation_filter == "encounter":
                rec.filtered_encounter_observation_ids = (
                    rec.encounter_observation_ids.filtered_domain(domain)
                )
                rec.filtered_patient_observation_ids = None
            else:
                rec.filtered_patient_observation_ids = (
                    rec.patient_observation_ids.filtered_domain(domain)
                )
                rec.filtered_encounter_observation_ids = None

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
        types = self.env["ni.observation.type"].with_context({"readonly_test": False})
        for f in VITALSIGN_FIELDS:
            if f in vals and vals[f]:
                ob_type = types.search([("code", "=", f.replace("_", "-"))])
                value = vals[f]
                if type(value) is float:
                    value = round(value, 2)
                vals_list.append(self._observation_vals(ts, ob_type, value))
        if ("body_height" in vals or "body_weight" in vals) and self.bmi:
            # write BMI if any change
            bmi_type = types.search([("code", "=", "bmi")])
            vals_list.append(self._observation_vals(ts, bmi_type, round(self.bmi, 2)))
        if vals_list:
            return self.env["ni.observation"].create(vals_list)

    def _observation_vals(self, occurrence, ob_type, value):
        return {
            "occurrence": occurrence,
            "patient_id": self.patient_id.id,
            "encounter_id": self.id,
            "type_id": ob_type.id,
            "value_type": ob_type.value_type,
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
    def _compute_observation_latest(self):
        observations = self.env["ni.encounter.observation"]
        for rec in self:
            vs_lines = observations.search(
                [
                    ("encounter_id", "=", rec.id),
                    ("category_id.code", "=", "vital-signs"),
                ]
            )
            lab_lines = observations.search(
                [("encounter_id", "=", rec.id), ("category_id.code", "=", "laboratory")]
            )
            rec.write(
                {
                    "observation_latest_count": len(rec.observation_latest_ids),
                    "observation_latest_vital_sign_ids": [
                        fields.Command.set(vs_lines.ids)
                    ],
                    "observation_latest_vital_sign_count": len(vs_lines),
                    "observation_latest_lab_ids": [fields.Command.set(lab_lines.ids)],
                    "observation_latest_lab_count": len(lab_lines),
                }
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
