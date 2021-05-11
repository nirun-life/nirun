#  Copyright (c) 2021 Piruin P.
from odoo import fields, models


class Patient(models.Model):
    _inherit = "ni.patient"

    spouse_id = fields.Many2one(
        "res.partner", domain=[("type", "=", "relate"), ("is_company", "=", False)]
    )
    child_ids = fields.Many2one(
        "res.partner", domain=[("type", "=", "relate"), ("is_company", "=", False)]
    )
