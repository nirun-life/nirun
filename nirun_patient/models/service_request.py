#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class ServiceRequest(models.Model):
    _name = "ni.service.request"
    _description = "Service Request"
    _inherit = ["ni.patient.res", "period.mixin"]

    service_id = fields.Many2one("ni.service")
    priority = fields.Selection(
        [("0", "Routine"), ("1", "Urgent"), ("2", "ASAP"), ("3", "STAT")],
        default="0",
        required=True,
    )
    state = fields.Selection(
        [
            ("draft", "Routine"),
            ("active", "Active"),
            ("on-hold", "On-hold"),
            ("revoked", "Revoked"),
            ("completed", "Completed"),
            ("entered-in-error", "Error"),
        ],
        default="draft",
        required=True,
    )

    user_id = fields.Many2one(
        "res.users", "Requester", default=lambda self: self.env.uid
    )
    instruction = fields.Text(help="Patient oriented instructions")
