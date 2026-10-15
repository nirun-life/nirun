#  Copyright (c) 2026 NSTDA

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    title_id = fields.Many2one("res.partner.title")
