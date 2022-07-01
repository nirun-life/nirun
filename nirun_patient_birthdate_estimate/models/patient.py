#  Copyright (c) 2021 NSTDA

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Patient(models.Model):
    _inherit = "ni.patient"

    birthdate_estimate = fields.Boolean(
        "Estimate Date of Birth",
        default=False,
        help="Indicate whether input birthday is estimated value, "
        "Exactly date of birth is unknown.",
    )

    @api.onchange("birthdate_estimate")
    def onchange_birthdate_estimate(self):
        if self.birthdate_estimate:
            date = self.birthdate or fields.Date.today()
            self.birthdate = date.replace(month=1, day=1)

    @api.constrains("birthdate", "birthdate_estimate")
    def _check_birthdate(self):
        for rec in self:
            if rec.birthdate_estimate and not rec._estimate_birthdate_format():
                raise UserError(_("Birth date must be 1 January"))

    def _estimate_birthdate_format(self):
        return self.birthdate.month == 1 and self.birthdate.day == 1
