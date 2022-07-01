#  Copyright (c) 2021 NSTDA

from odoo import models


class GoalCode(models.Model):
    _name = "ni.goal.code"
    _description = "Goal Code"
    _inherit = ["coding.base"]
