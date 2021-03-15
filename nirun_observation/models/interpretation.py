#  Copyright (c) 2021 Piruin P.

from odoo import models


class Interpretation(models.Model):
    _name = "ni.observation.interpretation"
    _description = "Interpretation"
    _inherit = ["coding.base"]
