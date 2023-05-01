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
