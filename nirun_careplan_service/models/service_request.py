#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class ServiceRequest(models.Model):
    _inherit = "ni.service.request"

    careplan_activity_id = fields.Many2one(
        "ni.careplan.activity", readonly=True, tracking=True
    )
    careplan_id = fields.Many2one(related="careplan_activity_id.careplan_id")
