#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    service_calendar_id = fields.Many2one(
        "resource.calendar", help="Default service resource calendar"
    )
