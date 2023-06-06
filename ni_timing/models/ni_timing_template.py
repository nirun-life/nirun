#  Copyright (c) 2021-2023 NSTDA

from odoo import fields, models


class TimingTemplate(models.Model):
    _name = "ni.timing.template"
    _description = "Timing Template"
    _inherit = ["ni.coding", "ni.timing.timing"]

    sequence = fields.Integer(copy=False)
    definition = fields.Text(copy=False)
    color = fields.Integer(copy=False)
    active = fields.Boolean(copy=False)
    abbr = fields.Char(copy=False)
    system_id = fields.Many2one(copy=False)

    name = fields.Text("Template Name", compute=None, store=True, copy=False)
    when = fields.Many2many(
        "ni.timing.event", "ni_timing_template_event_rel", "template_id", "event_id"
    )
    day_of_week = fields.Many2many(
        "ni.timing.dow", "ni_timing_template_dow_rel", "template_id", "dow_id"
    )
    time_of_day = fields.One2many("ni.timing.template.tod", "timing_id")

    def to_timing(self, default=None):
        self.ensure_one()
        vals = self.copy_data(default)
        return self.env["ni.timing.timing"].create(vals)
