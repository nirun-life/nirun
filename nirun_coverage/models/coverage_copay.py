#  Copyright (c) 2021 Piruin P.

from odoo import models


class CopayType(models.Model):
    _name = "ni.coverage.copay"
    _description = "Copay Type"
    _inherit = ["coding.base"]
