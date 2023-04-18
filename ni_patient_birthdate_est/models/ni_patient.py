#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    birthdate_estimate = fields.Boolean(
        related="partner_id.birthdate_estimate", readonly=False
    )

    @api.onchange("birthdate_estimate")
    def onchange_birthdate_estimate(self):
        if self.birthdate_estimate:
            date = self.birthdate or fields.Date.today()
            self.birthdate = date.replace(month=1, day=1)
