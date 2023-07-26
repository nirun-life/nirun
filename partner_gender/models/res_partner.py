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

    @api.onchange("title")
    def _onchange_title(self):
        if self.title and self.title.gender:
            self.gender = self.title.gender
