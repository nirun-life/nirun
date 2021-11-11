#  Copyright (c) 2021 Piruin P.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Patient(models.Model):
    _inherit = "ni.patient"

    identification_id_na = fields.Boolean("N/A", default=False)

    @api.onchange("identification_id")
    def _onchange_identification_id_for_na(self):
        if self.identification_id:
            self.update({"identification_id_na": False})

    @api.constrains("identification_id", "identification_id_na")
    def _check_identification_id_na(self):
        for rec in self:
            if rec.identification_id_na and rec.identification_id:
                raise ValidationError(
                    _("Identification ID (%s) must be empty if N/A is checked")
                    % rec.identification_id
                )
