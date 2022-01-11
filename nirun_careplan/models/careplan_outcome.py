#  Copyright (c) 2021 Piruin P.

from odoo import models


class CarePlanOutcome(models.Model):
    _name = "ni.careplan.outcome"
    _description = "Careplan Outcome"
    _inherit = ["coding.base"]
