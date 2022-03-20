#  Copyright (c) 2021 Piruin P.

from odoo import models


class ConditionClass(models.Model):
    _name = "ni.condition.cls"
    _description = "Condition / Problem Classification"
    _inherit = ["coding.base"]
