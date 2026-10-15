#  Copyright (c) 2026 NSTDA
#  Based on res.partner.title from Odoo 18.0 (Odoo S.A., LGPL-3).

from odoo import fields, models


class PartnerTitle(models.Model):
    _name = "res.partner.title"
    _order = "name"
    _description = "Partner Title"

    name = fields.Char(string="Title", required=True, translate=True)
    shortcut = fields.Char(string="Abbreviation", translate=True)
