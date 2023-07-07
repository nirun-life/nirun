#  Copyright (c) 2023 NSTDA
from odoo import fields, models


class EncounterClass(models.Model):
    _inherit = "ni.encounter.class"

    summary_report_title = fields.Char()
