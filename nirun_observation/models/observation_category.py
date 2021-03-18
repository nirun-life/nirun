#  Copyright (c) 2021 Piruin P.
from odoo import models


class ObservationType(models.Model):
    _name = "ni.observation.category"
    _description = "Observation Category"
    _inherit = ["coding.base"]
