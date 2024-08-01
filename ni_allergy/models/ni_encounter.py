#  Copyright (c) 2022-2023 NSTDA

from odoo import models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    def action_view_allergy(self):
        return self.patient_id.action_view_allergy(
            ctx={"default_encounter_id": self.id}
        )

    def action_add_allergy(self):
        return self.patient_id.action_add_allergy(ctx={"default_encounter_id": self.id})
