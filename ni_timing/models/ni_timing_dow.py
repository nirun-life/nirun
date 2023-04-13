#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class DayOfWeek(models.Model):
    _name = "ni.timing.dow"
    _description = "Day of Week"
    _inherit = ["ni.coding"]
