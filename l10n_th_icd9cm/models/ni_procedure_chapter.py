#  Copyright (c) 2023 NSTDA

from odoo import _, api, fields, models


class ProcedureChapter(models.Model):
    _name = "ni.procedure.chapter"
    _description = "Procedure Chapter"
    _inherit = "ni.coding"

    chapter = fields.Char()
    display_name = fields.Char(compute="_compute_display_name", store=True)
    code_ids = fields.One2many("ni.procedure.code", "chapter_id")

    @api.depends("chapter", "name", "code")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = _("{}. {} ({})".format(rec.chapter, rec.name, rec.code))
