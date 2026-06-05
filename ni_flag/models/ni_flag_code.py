#  Copyright (c) 2026 NSTDA
from odoo import api, fields, models


class FlagCode(models.Model):
    _name = "ni.flag.code"
    _description = "Flag Code"
    _inherit = ["ni.coding"]

    patient_count = fields.Integer(compute="_compute_patient_count")

    @api.depends_context("company")
    def _compute_patient_count(self):
        data = self.env["ni.flag"].read_group(
            [("code_id", "in", self.ids), ("status", "=", "active")],
            ["code_id", "patient_id:count_distinct"],
            ["code_id"],
        )
        mapped = {d["code_id"][0]: d["patient_id"] for d in data}
        for rec in self:
            rec.patient_count = mapped.get(rec.id, 0)

    def action_view_patients(self):
        self.ensure_one()
        active_flags = self.env["ni.flag"].search(
            [("code_id", "=", self.id), ("status", "=", "active")]
        )
        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "ni.patient",
            "view_mode": "kanban,tree,form",
            "domain": [("id", "in", active_flags.mapped("patient_id").ids)],
        }
