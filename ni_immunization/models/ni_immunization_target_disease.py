#  Copyright (c) 2026 NSTDA
from odoo import _, fields, models


class ImmunizationTargetDisease(models.Model):
    _name = "ni.immunization.target.disease"
    _description = "Immunization Target Disease"
    _inherit = ["ni.coding"]

    series_doses = fields.Integer("Doses Required", default=1)

    def action_evaluation(self):
        self.ensure_one()
        return {
            "name": _("New Evaluation — %s") % self.display_name,
            "type": "ir.actions.act_window",
            "res_model": "ni.immunization.evaluation",
            "view_mode": "form",
            "context": {
                **self.env.context,
                "default_target_disease_id": self.id,
            },
        }
