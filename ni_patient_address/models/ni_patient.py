#  Copyright (c) 2021-2023 NSTDA

from odoo import api, models


class Patient(models.Model):
    _inherit = "ni.patient"

    @api.onchange("country_id")
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange("state_id")
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id
