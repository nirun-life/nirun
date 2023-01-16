#  Copyright (c) 2023. NSTDA
from odoo import api, models


class Partner(models.Model):
    _inherit = "res.partner"

    @api.constrains("zip_id", "country_id", "city_id", "state_id")
    def _check_zip(self):
        if self.patient:
            self.patient_id._check_zip()
        else:
            super()._check_zip()
