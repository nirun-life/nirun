from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    line = fields.Char("LINE ID")

    _sql_constraints = {
        ("line_uniq", "UNIQUE(line)", "LINE ID must be unique"),
    }
