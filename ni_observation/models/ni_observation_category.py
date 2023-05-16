#  Copyright (c) 2021 NSTDA
from odoo import models


class ObservationType(models.Model):
    _name = "ni.observation.category"
    _description = "Observation Category"
    _inherit = ["ni.coding"]
