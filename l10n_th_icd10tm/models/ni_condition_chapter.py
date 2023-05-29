#  Copyright (c) 2021-2023 NSTDA

from odoo import _, api, fields, models


class ConditionChappter(models.Model):
    _name = "ni.condition.chapter"
    _inherit = "ni.coding"

    roman = fields.Char()
    display_name = fields.Char(compute="_compute_display_name", store=True)
    block_ids = fields.One2many("ni.condition.block", "chapter_id")

    @api.depends("roman", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = _(
                "Chapter {} {} ({})".format(rec.roman, rec.name, rec.code)
            )
