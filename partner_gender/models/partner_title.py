#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class PartnerTitle(models.Model):
    _inherit = "res.partner.title"

    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")],
        help="default gender for this Title",
        default=None,
    )
