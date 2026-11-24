#  Copyright (c) 2022-2023 NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    document_ids = fields.One2many("ni.document.ref", "encounter_id")
    document_count = fields.Integer(compute="_compute_document_count")

    @api.depends("document_ids")
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = len(rec.document_ids)

    def action_document_ref(self):
        action_rec = self.env.ref("ni_document_ref.ni_document_ref_action").sudo()
        action = action_rec.read()[0]
        ctx = dict(self.env.context)
        ctx.update(
            {
                "search_default_group_by_encounter": 1,
                "default_patient_id": self[0].patient_id.id,
                "default_encounter_id": self.ids[0],
            }
        )
        action["context"] = ctx
        action["domain"] = [("patient_id", "=", self[0].patient_id.id)]
        return action
