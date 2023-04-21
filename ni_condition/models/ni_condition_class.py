#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class ConditionClass(models.Model):
    _name = "ni.condition.class"
    _description = "Condition / Problem Classification"
    _inherit = ["ni.coding"]
