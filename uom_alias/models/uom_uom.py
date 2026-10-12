#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class UoM(models.Model):
    _inherit = "uom.uom"
    _rec_names_search = ["name", "alias"]

    alias = fields.Char()
