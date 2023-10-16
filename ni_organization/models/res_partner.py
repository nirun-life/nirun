#  Copyright (c) 2023 NSTDA
from odoo import _, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    identifier = fields.Char()

    _sql_constraints = [
        (
            "identifier_unique",
            "unique (identifier)",
            _("This identifier already exist!"),
        ),
    ]
