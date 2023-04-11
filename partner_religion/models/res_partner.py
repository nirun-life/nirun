#  Copyright (c) 2023 NSTDA
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    religion_id = fields.Many2one("res.religion")
