#  Copyright (c) 2026 NSTDA
#  Based on res.partner from Odoo 18.0 base and phone_validation (Odoo S.A., LGPL-3).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    mobile = fields.Char()

    @api.onchange("mobile", "country_id", "company_id")
    def _onchange_mobile_validation(self):
        if self.mobile:
            self.mobile = (
                self._phone_format(fname="mobile", force_format="INTERNATIONAL")
                or self.mobile
            )
