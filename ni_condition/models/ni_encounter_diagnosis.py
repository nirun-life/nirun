#  Copyright (c) 2023 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import UserError


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
    role_id = fields.Many2one(
        "ni.encounter.diagnosis.role",
        ondelete="restrict",
        domain="[('system_id', '=', system_id)]",
    )
    role_decoration = fields.Selection(related="role_id.decoration")
    condition_id = fields.Many2one("ni.condition", required=True, ondelete="restrict")
    is_problem_editable = fields.Boolean(compute="_compute_is_problem_editable")

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
                raise UserError(_("Encounter Diagnosis must specify role"))

    @api.constrains("is_diagnosis", "is_problem")
    def _check_is_diagnosis_or_problem(self):
        for rec in self:
            if not rec.is_diagnosis and not rec.is_problem:
                raise UserError(
                    _(
                        "Diagnosis line must be at least a Diagnosis or a Problem-List Item"
                    )
                )

    @api.depends(
        "condition_id.diagnosis_ids.encounter_start",
        "condition_id.diagnosis_ids.is_problem",
        "encounter_id",
    )
    def _compute_is_problem_editable(self):
        for rec in self:
            lines = rec.condition_id.diagnosis_ids
            if not lines:
                rec.is_problem_editable = True
                continue
            origin = min(
                lines,
                key=lambda line: (
                    line.encounter_start or fields.Datetime.now(),
                    line.id,
                ),
            )
            rec.is_problem_editable = (
                not origin.is_problem or origin.encounter_id == rec.encounter_id
            )

    def action_toggle_is_diagnosis(self):
        self.ensure_one()
        if not self.is_diagnosis:
            if not self.role_id:
                action = self.env["ir.actions.act_window"]._for_xml_id(
                    "ni_condition.ni_encounter_diagnosis_role_wizard_action"
                )
                action["context"] = {"default_diagnosis_id": self.id}
                return action
            self.is_diagnosis = True
        else:
            self.write({"is_diagnosis": False, "role_id": False})
        return True

    def action_toggle_is_problem(self):
        for rec in self:
            if not rec.is_problem_editable:
                raise UserError(
                    _(
                        "Problem-List status was set in a prior encounter and can't be changed here"
                    )
                )
            rec.is_problem = not rec.is_problem

    def unlink(self):
        condition_ids = self.mapped("condition_id")
        res = super().unlink()
        return res & condition_ids.unlink()
