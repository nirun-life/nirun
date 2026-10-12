#  Copyright (c) 2023 NSTDA
from odoo import fields, models


class NiIdentifierTest(models.Model):
    _module = None
    _name = "ni.identifier.test"
    _inherit = ["ni.identifier.mixin"]
    _description = "Identifier Mixin Test"

    name = fields.Char()
