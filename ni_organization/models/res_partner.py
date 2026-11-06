#  Copyright (c) 2023 NSTDA
from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    identifier = fields.Char()

    _sql_constraints = [
        (
            "identifier_unique",
            "unique (identifier)",
            "This identifier already exist!",
        ),
    ]
