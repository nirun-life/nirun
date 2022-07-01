#  Copyright (c) 2021 NSTDA

from odoo import fields, models


class TimingTimeOfDay(models.Model):
    _name = "ni.timing.tod"
    _description = "Time of Day"
    timing_id = fields.Many2one("ni.timing", required=True)
    value = fields.Float("Time")
