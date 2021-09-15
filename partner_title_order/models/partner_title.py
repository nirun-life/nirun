#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class PartnerTitle(models.Model):
    _inherit = "res.partner.title"
    _order = "sequence"

    sequence = fields.Integer(index=True, default=0)
