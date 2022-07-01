#  Copyright (c) 2021 NSTDA
from odoo import models


class Partner(models.Model):
    _inherit = "res.partner"

    def action_patient_record(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "views": [[False, "form"]],
            "res_model": "ni.patient",
            "res_id": self.patient_id.id,
            "context": {"default_partner_id": self.id},
        }
