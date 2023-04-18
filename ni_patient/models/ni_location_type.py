#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class LocationType(models.Model):
    _name = "ni.location.type"
    _description = "Location Types"
    _inherit = ["ni.coding"]
