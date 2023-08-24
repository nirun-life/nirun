#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Encounter(models.Model):
    _inherit = "ni.encounter"

    diagnosis_ids = fields.One2many("ni.encounter.diagnosis", "encounter_id")
    diagnosis_count = fields.Integer(compute="_compute_diagnosis_count")

    def action_confirm(self):
        super(Encounter, self).action_confirm()
        for rec in self:
            if not rec.diagnosis_ids:
                prob = self.env["ni.condition"].search(
                    [("patient_id", "=", rec.patient_id.id), ("is_problem", "=", True)]
                )
                if prob:
                    vals = {
                        "diagnosis_ids": [
                            fields.Command.create(
                                {
                                    "encounter_id": rec.id,
                                    "condition_id": p.id,
                                    "patient_id": rec.patient_id.id,
                                    "code_id": p.code_id.id,
                                    "is_problem": True,
                                }
                            )
                            for p in prob
                        ]
                    }
                    rec.write(vals)

    @api.depends("diagnosis_ids")
    def _compute_diagnosis_count(self):
        procedure = self.env["ni.encounter.diagnosis"].sudo()
        read = procedure.read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["encounter_id"]
        )
        data = {res["encounter_id"][0]: res["encounter_id_count"] for res in read}
        for encounter in self:
            encounter.diagnosis_count = data.get(encounter.id, 0)

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
