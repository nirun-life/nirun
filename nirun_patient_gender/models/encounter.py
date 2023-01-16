#  Copyright (c) 2021-2023. NSTDA

from odoo import api, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    @api.onchange("title")
    def _onchange_title(self):
        if self.title and self.title.gender:
            self.gender = self.title.gender
