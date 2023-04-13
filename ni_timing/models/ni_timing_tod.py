#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class TimeOfDay(models.Model):
    _name = "ni.timing.tod"
    _description = "Time of Day Coding"
    _inherit = ["ni.timing.timing.tod", "ni.coding"]

    timing_id = fields.Many2one("ni.timing.timing", required=False, store=False)
