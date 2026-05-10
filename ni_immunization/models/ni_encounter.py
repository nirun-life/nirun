#  Copyright (c) 2026 NSTDA
from odoo import _, fields, models

from odoo.addons.ni_patient.models.ni_encounter import LOCK_STATE_DICT


class Encounter(models.Model):
    _inherit = "ni.encounter"

    show_immunization = fields.Boolean(related="class_id.immunization")
    immunization_ids = fields.One2many(
        "ni.immunization", "encounter_id", states=LOCK_STATE_DICT
    )
    immunization_count = fields.Integer(compute="_compute_immunization_count")
    evaluation_ids = fields.One2many(
        "ni.immunization.evaluation", "encounter_id", states=LOCK_STATE_DICT
    )

    def _compute_immunization_count(self):
        immunization = self.env["ni.immunization"].sudo()
        read = immunization.read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["encounter_id"]
        )
        data = {res["encounter_id"][0]: res["encounter_id_count"] for res in read}
        for enc in self:
            enc.immunization_count = data.get(enc.id, 0)

    def action_immunization(self):
        action = {
            "name": _("Immunization History"),
            "type": "ir.actions.act_window",
            "res_model": "ni.immunization",
            "view_mode": "tree,kanban,form",
            "context": {
                "search_default_group_by_encounter": 1,
                "default_patient_id": self[0].patient_id.id,
                "default_encounter_id": self.ids[0],
            },
            "domain": [("patient_id", "=", self[0].patient_id.id)],
        }
        return action
