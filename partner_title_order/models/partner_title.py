#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class PartnerTitle(models.Model):
    _inherit = "res.partner.title"
    _order = "sequence"

    sequence = fields.Integer(index=True, default=99)
