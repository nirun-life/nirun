#  Copyright (c) 2021 Piruin P.

from odoo import models


class LocationType(models.Model):
    _name = "ni.location.type"
    _description = "Location Types"
    _inherit = ["coding.base"]
