#  Copyright (c) 2021 NSTDA

from odoo import models


class TimingDayOfWeek(models.Model):
    _name = "ni.timing.dow"
    _description = "Day of Week"
    _inherit = ["coding.base"]
