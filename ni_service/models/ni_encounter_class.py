#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class EncounterClass(models.Model):
    _inherit = "ni.encounter.class"

    service_calendar_id = fields.Many2one("resource.calendar")
    service_ids = fields.Many2many("ni.service", help="Default Service")
