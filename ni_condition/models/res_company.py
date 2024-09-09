#  Copyright (c) 2024 NSTDA

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    condition_system_ids = fields.Many2many(
        "ni.coding.system",
        default=lambda self: [(6, 0, [self.env.ref("ni_coding.system_internal").id])],
    )
