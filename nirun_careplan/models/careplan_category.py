#  Copyright (c) 2021 Piruin P.

from odoo import models


class CarePlanCategory(models.Model):
    _name = "ni.careplan.category"
    _description = "Careplan Category"
    _inherit = ["coding.base"]
