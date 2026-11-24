#  Copyright (c) 2023 NSTDA
from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "ni.identifier.mixin"]

    period_start = fields.Datetime()
