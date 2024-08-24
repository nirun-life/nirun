#  Copyright (c) 2024 NSTDA
from odoo import api, fields, models


class MedicationRequest(models.Model):
    _inherit = "ni.medication.request"

    @api.model
    def default_get(self, fields):
        res = super(MedicationRequest, self).default_get(fields)
        if "careplan_id" in res:
            res["intent"] = "plan"
        return res

    careplan_id = fields.Many2one("ni.careplan", index=True, ondelete="cascade")

    @api.constrains("careplan_id", "encounter_id")
    def _check_careplan_encounter(self):
        for rec in self:
            if rec.careplan_id and rec.encounter_id:
                # We don't want SR to show on Encounter order when it was created from careplan
                rec.encounter_id = None
