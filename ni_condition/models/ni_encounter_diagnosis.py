#  Copyright (c) 2023 NSTDA

from odoo import _, api, fields, models


class Diagnosis(models.Model):
    _name = "ni.encounter.diagnosis"
    _description = "Diagnosis"
    _inherits = {"ni.condition": "condition_id"}

    _order = "sequence,create_date"

    sequence = fields.Integer()
    encounter_id = fields.Many2one(
        "ni.encounter",
        related="condition_id.encounter_id",
        store=True,
        required=True,
        readonly=False,
        ondelete="cascade",
    )
    role_id = fields.Many2one("ni.encounter.diagnosis.role", ondelete="restrict")
    role_decoration = fields.Selection(related="role_id.decoration")
    condition_id = fields.Many2one("ni.condition", required=True, ondelete="cascade")

    _sql_constraints = [
        (
            "encounter_condition_uniq",
            "unique (encounter_id, condition_id)",
            _("Condition must be unique!"),
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "is_diagnosis" not in vals:
                vals["is_diagnosis"] = True
            if "code_id" in vals:
                #  Check code already exist as problem history that just reveal on this encounter
                problem_id = self.env["ni.condition"].search(
                    [
                        ("encounter_id", "=", vals["encounter_id"]),
                        ("code_id", "=", vals["code_id"]),
                        ("is_problem", "=", True),
                    ],
                    limit=1,
                )
                if problem_id:
                    vals.update(
                        {
                            "is_problem": True,
                            "condition_id": problem_id.id,
                        }
                    )
        return super().create(vals_list)

    @api.onchange("role_id")
    def _onchange_role_id(self):
        if self.role_id:
            self.sequence = self.role_id.sequence
        else:
            self.sequence = 99

    @api.onchange("is_diagnosis")
    def _onchange_is_diagnosis(self):
        if not self.is_diagnosis and self.role_id:
            self.role_id = None

    @api.onchange("class_id")
    def _onchange_class_id(self):
        if self.class_id:
            self.sequence = self.class_id.sequence

    @api.constrains("is_diagnosis", "role_id")
    def _check_is_diagnosis(self):
        for rec in self:
            if rec.is_diagnosis and not rec.role_id:
                raise _("Encounter Diagnosis must specify role")

    def unlink(self):
        condition_ids = self.mapped("condition_id")
        res = super().unlink()
        return res & condition_ids.unlink()
