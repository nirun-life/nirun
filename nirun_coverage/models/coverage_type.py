#  Copyright (c) 2021 Piruin P.

from odoo import models


class CopayType(models.Model):
    _name = "ni.coverage.type"
    _description = "Coverage Type"
    _inherit = ["coding.base"]
