#  Copyright (c) 2021 NSTDA

from odoo import models


class TimingEvent(models.Model):
    _name = "ni.timing.event"
    _description = "Timing Event"
    _inherit = ["coding.base"]
