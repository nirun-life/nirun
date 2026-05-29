#  Copyright (c) 2026 NSTDA
from odoo import api, fields, models


class Patient(models.Model):
    _name = "ni.patient"
    _inherit = "ni.patient"

    flag_ids = fields.One2many(
        "ni.flag", "patient_id", string="Flags", check_company=True
    )
    flag_count = fields.Integer(compute="_compute_flag_count")
    active_flag_ids = fields.One2many(
        "ni.flag",
        "patient_id",
        domain=[("status", "=", "active")],
        string="Active Flags",
    )

    @api.depends("flag_ids.status")
    def _compute_flag_count(self):
        data = self.env["ni.flag"].read_group(
            [("patient_id", "in", self.ids), ("status", "=", "active")],
            ["patient_id"],
            ["patient_id"],
        )
        mapped = {d["patient_id"][0]: d["patient_id_count"] for d in data}
        for rec in self:
            rec.flag_count = mapped.get(rec.id, 0)

    def action_flag(self):
        self.ensure_one()
        return {
            "name": "Flags",
            "type": "ir.actions.act_window",
            "res_model": "ni.flag",
            "view_mode": "tree,form",
            "domain": [("patient_id", "=", self.id)],
            "context": {
                "default_patient_id": self.id,
                "search_default_active": True,
            },
        }
