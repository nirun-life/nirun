#  Copyright (c) 2021-2023. NSTDA

from odoo import api, models


class Patient(models.Model):
    _inherit = "ni.encounter"

    @api.onchange("identification_id")
    def _onchange_identification_id_for_na(self):
        if self.identification_id:
            self.update({"identification_id_na": False})
