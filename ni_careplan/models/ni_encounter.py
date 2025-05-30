#  Copyright (c) 2025 NSTDA
from odoo import models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    def action_new_careplan(self):
        self.ensure_one()
        context = dict(self.env.context)
        context.update({"default_encounter_id": self.id})
        return self.with_context(context).patient_id.action_new_careplan()
