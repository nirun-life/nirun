#  Copyright (c) 2024 NSTDA
from odoo import models


class GoalCategory(models.Model):
    _name = "ni.goal.category"
    _description = "Goal Category"
    _inherit = "ni.coding"
