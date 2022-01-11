#  Copyright (c) 2021 Piruin P.

from odoo import models


class GoalCode(models.Model):
    _name = "ni.goal.code"
    _description = "Goal Code"
    _inherit = ["coding.base"]
