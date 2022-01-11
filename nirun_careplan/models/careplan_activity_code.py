#  Copyright (c) 2021 Piruin P.

from odoo import models


class ActivityCode(models.Model):
    _name = "ni.careplan.activity.code"
    _description = "Careplan Activity Code"
    _inherit = ["coding.base"]
