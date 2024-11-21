#  Copyright (c) 2022-2023 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Encounter(models.Model):
    _inherit = "ni.encounter"

    def action_view_allergy(self):
        return self.patient_id.action_view_allergy(
            ctx={"default_encounter_id": self.id}
        )

    def action_add_allergy(self):
        return self.patient_id.action_add_allergy(ctx={"default_encounter_id": self.id})

    @api.constrains("allergy_ids", "allergy")
    def _check_allergy(self):
        for rec in self:
            if rec.allergy != "identified" and rec.allergy_ids:
                rec.allergy_ids = [fields.Command.clear()]
            if rec.allergy == "identified" and not rec.allergy_ids:
                raise UserError(_("Must identify at least one allergy record"))
