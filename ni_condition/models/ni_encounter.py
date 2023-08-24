#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Encounter(models.Model):
    _inherit = "ni.encounter"

    condition_ids = fields.One2many(
        "ni.condition", "encounter_id", string="Condition", readonly=True
    )
    condition_prev_ids = fields.One2many(
        "ni.condition",
        string="Previous Diagnosis",
        compute="_compute_condition_prev_ids",
        readonly=True,
    )
    diagnosis_ids = fields.One2many("ni.encounter.diagnosis", "encounter_id")
    diagnosis_count = fields.Integer(compute="_compute_diagnosis_count")

    @api.depends("diagnosis_ids")
    def _compute_diagnosis_count(self):
        procedure = self.env["ni.encounter.diagnosis"].sudo()
        read = procedure.read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["encounter_id"]
        )
        data = {res["encounter_id"][0]: res["encounter_id_count"] for res in read}
        for encounter in self:
            encounter.diagnosis_count = data.get(encounter.id, 0)

    @api.depends("patient_id")
    def _compute_condition_prev_ids(self):
        conditions = self.env["ni.condition"]
        for rec in self:
            rec.condition_prev_ids = conditions.search(
                [
                    ("patient_id", "=", self.patient_id.id),
                    ("encounter_id", "<", rec.id),
                    ("is_diagnosis", "=", True),
                ],
                order="encounter_id desc",
            )

    @api.constrains("encounter_id", "diagnosis_ids")
    def _check_role_limit(self):
        for rec in self:
            if not rec.diagnosis_ids:
                continue
            roles = rec.diagnosis_ids.mapped("role_id").filtered_domain(
                [("limit", ">", 0)]
            )
            for role in roles:
                role_count = len(
                    rec.diagnosis_ids.filtered_domain([("role_id", "=", role.id)])
                )
                if role_count > role.limit:
                    raise ValidationError(
                        _(
                            "Diagnosis as [{}] has reached limit at {} item".format(
                                role.name, role.limit
                            )
                        )
                    )

    def action_condition(self):
        self.ensure_one()
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_group_by_encounter": 1,
                "default_patient_id": self[0].patient_id.id,
                "default_encounter_id": self[0].id,
            }
        )
        view = {
            "name": _("Problem List"),
            "res_model": "ni.condition",
            "type": "ir.actions.act_window",
            "target": "current",
            "view_mode": "tree,form",
            "domain": [("patient_id", "=", self.patient_id.id)],
            "context": ctx,
        }
        return view
