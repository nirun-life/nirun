#  Copyright (c) 2021-2023 NSTDA

from odoo import _, models


class PartnerTitle(models.Model):
    _inherit = "res.partner.title"

    _sql_constraints = [
        (
            "name_unique",
            "unique (name)",
            _("This title already exist!"),
        ),
    ]
