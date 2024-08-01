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
        store=True,
        required=True,
        readonly=False,
        ondelete="cascade",
    )
    encounter_start = fields.Datetime(related="encounter_id.period_start")
    role_id = fields.Many2one("ni.encounter.diagnosis.role", ondelete="restrict")
    role_decoration = fields.Selection(related="role_id.decoration")
    condition_id = fields.Many2one("ni.condition", required=True, ondelete="restrict")

    _sql_constraints = [
        (
            "encounter_id_condition_id_uniq",
            "unique (encounter_id, condition_id)",
            _("Condition must be unique!"),
        ),
    ]

    @api.onchange("code_id")
    def _onchange_code_id(self):
        for rec in self.filtered(lambda r: r.code_id):
            rec.name = rec.code_id.name

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "code_id" in vals and "condition_id" not in vals:
                enc = self.env["ni.encounter"].browse(vals["encounter_id"])
                condition = self.env["ni.condition"].search(
                    [
                        ("patient_id", "=", enc.patient_id.id),
                        ("code_id", "=", vals["code_id"]),
                    ],
                    limit=1,
                )
                if condition:
                    vals.update({"condition_id": condition.id})
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

    @api.constrains("is_diagnosis", "role_id")
    def _check_is_diagnosis(self):
        for rec in self:
            if rec.is_diagnosis and not rec.role_id:
                raise _("Encounter Diagnosis must specify role")

    def unlink(self):
        condition_ids = self.mapped("condition_id")
        res = super().unlink()
        return res & condition_ids.unlink()
