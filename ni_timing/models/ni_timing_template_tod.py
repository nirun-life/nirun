#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class TimingTemplateTimeOfDay(models.Model):
    _name = "ni.timing.template.tod"
    _description = "Time of Day"
    _inherit = ["ni.timing.timing.tod"]

    timing_id = fields.Many2one("ni.timing.template", ondelete="cascade")
