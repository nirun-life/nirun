#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class TimingTemplate(models.Model):
    _name = "ni.timing.template"
    _description = "Timing Template"
    _inherit = ["coding.base", "ni.timing"]

    name = fields.Char("Template Name", compute=None, store=True)
    when = fields.Many2many(
        "ni.timing.event", "ni_timing_template_event_rel", "timing_tmpl_id", "event_id"
    )
    day_of_week = fields.Many2many(
        "ni.timing.dow", "ni_timing_template_dow_rel", "timing_tmpl_id", "dow_id"
    )
