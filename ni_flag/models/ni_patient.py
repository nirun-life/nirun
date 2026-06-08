#  Copyright (c) 2026 NSTDA
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class Patient(models.Model):
    _name = "ni.patient"
    _inherit = "ni.patient"

    flag_ids = fields.One2many(
        "ni.flag", "patient_id", string="Flag Records", check_company=True
    )
    active_flag_ids = fields.One2many(
        "ni.flag",
        "patient_id",
        domain=[("status", "=", "active"), ("encounter_id", "=", False)],
        string="Active Flags",
    )
    flag_code_ids = fields.Many2many(
        "ni.flag.code",
        compute="_compute_flag_code_ids",
        inverse="_inverse_flag_code_ids",
        string="Flags",
    )

    @api.depends("flag_ids.status", "flag_ids.code_id", "flag_ids.encounter_id")
    def _compute_flag_code_ids(self):
        for rec in self:
            active = rec.flag_ids.filtered(
                lambda f: f.status == "active" and not f.encounter_id
            )
            rec.flag_code_ids = active.mapped("code_id")

    def _inverse_flag_code_ids(self):
        Flag = self.env["ni.flag"]
        for rec in self:
            active = rec.flag_ids.filtered(
                lambda f: f.status == "active" and not f.encounter_id
            )
            current_codes = active.mapped("code_id")
            to_add = rec.flag_code_ids - current_codes
            to_remove = active.filtered(lambda f: f.code_id not in rec.flag_code_ids)
            for code in to_add:
                Flag.create({"patient_id": rec.id, "code_id": code.id})
            to_remove.action_inactive()

    def action_manage_flags(self):
        self.ensure_one()
        action = self.env.ref("ni_flag.ni_patient_flag_action").read()[0]
        action["domain"] = [("patient_id", "=", self.id)]
        action_context = action.get("context")
        context = (
            safe_eval(action_context)
            if isinstance(action_context, str)
            else dict(action_context or {})
        )
        context.update(self.env.context)
        context.update(
            {
                "default_patient_id": self.id,
            }
        )
        action["context"] = context
        return action
