#  Copyright (c) 2026 NSTDA
from odoo import api, fields, models


class Encounter(models.Model):
    _name = "ni.encounter"
    _inherit = "ni.encounter"

    flag_ids = fields.One2many(
        "ni.flag", "encounter_id", string="Flags", check_company=True
    )
    flag_count = fields.Integer(compute="_compute_flag_count")

    @api.depends("flag_ids.status")
    def _compute_flag_count(self):
        data = self.env["ni.flag"].read_group(
            [("encounter_id", "in", self.ids), ("status", "=", "active")],
            ["encounter_id"],
            ["encounter_id"],
        )
        mapped = {d["encounter_id"][0]: d["encounter_id_count"] for d in data}
        for rec in self:
            rec.flag_count = mapped.get(rec.id, 0)

    def action_flag(self):
        self.ensure_one()
        return {
            "name": "Flags",
            "type": "ir.actions.act_window",
            "res_model": "ni.flag",
            "view_mode": "tree,form",
            "domain": [("encounter_id", "=", self.id)],
            "context": {
                "default_patient_id": self.patient_id.id,
                "default_encounter_id": self.id,
                "search_default_active": True,
            },
        }
