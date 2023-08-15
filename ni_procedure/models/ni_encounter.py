#  Copyright (c) 2022. NSTDA

from odoo import _, fields, models

from odoo.addons.ni_patient.models.ni_encounter import LOCK_STATE_DICT


class Encounter(models.Model):
    _inherit = "ni.encounter"

    procedure_ids = fields.One2many(
        "ni.procedure", "encounter_id", states=LOCK_STATE_DICT
    )
    procedure_count = fields.Integer(compute="_compute_procedure_count")

    def _compute_procedure_count(self):
        procedure = self.env["ni.procedure"].sudo()
        read = procedure.read_group(
            [("encounter_id", "in", self.ids)], ["encounter_id"], ["encounter_id"]
        )
        data = {res["encounter_id"][0]: res["encounter_id_count"] for res in read}
        for encounter in self:
            encounter.procedure_count = data.get(encounter.id, 0)

    def action_procedure(self):
        action = {
            "name": _("Procedure History"),
            "type": "ir.actions.act_window",
            "res_model": "ni.procedure",
            "view_mode": "tree,kanban,form,graph,pivot",
            "context": {
                "search_default_group_by_encounter": 1,
                "default_patient_id": self[0].patient_id.id,
                "default_encounter_id": self.ids[0],
            },
            "domain": [("patient_id", "=", self[0].patient_id.id)],
        }
        return action
