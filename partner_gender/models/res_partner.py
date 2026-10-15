#  Copyright (c) 2021-2023 NSTDA

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")],
        index=True,
        tracking=True,
        required=False,
    )

    @api.onchange("title_id")
    def _onchange_title_id(self):
        if self.title_id and self.title_id.gender:
            self.gender = self.title_id.gender
