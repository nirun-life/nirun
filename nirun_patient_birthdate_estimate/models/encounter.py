#  Copyright (c) 2023-2023. NSTDA

from odoo import api, fields, models


class Encounter(models.Model):
    _inherit = "ni.encounter"

    @api.onchange("birthdate_estimate")
    def onchange_birthdate_estimate(self):
        if self.birthdate_estimate:
            date = self.birthdate or fields.Date.today()
            self.birthdate = date.replace(month=1, day=1)
