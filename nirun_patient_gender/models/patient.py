#  Copyright (c) 2021 NSTDA

from odoo import api, models


class Patient(models.Model):
    _inherit = "ni.patient"

    @api.onchange("title")
    def _onchange_title(self):
        if self.title and self.title.gender:
            self.gender = self.title.gender
