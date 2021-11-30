#  Copyright (c) 2021 Piruin P.

from odoo import models


class TimingEvent(models.Model):
    _name = "ni.timing.event"
    _description = "Timing Event"
    _inherit = ["coding.base"]
