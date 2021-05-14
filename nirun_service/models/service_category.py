#  Copyright (c) 2021 Piruin P.

from odoo import models


class HealthcareServiceCategory(models.Model):
    _name = "ni.service.category"
    _description = "Healthcare Service Category"
    _inherit = ["coding.base"]
