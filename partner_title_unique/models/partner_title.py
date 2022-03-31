#  Copyright (c) 2021 Piruin P.

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
