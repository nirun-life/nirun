#  Copyright (c) 2021-2023 NSTDA

from odoo import models


class Event(models.Model):
    _name = "ni.timing.event"
    _description = "Timing Event"
    _inherit = ["ni.coding"]
