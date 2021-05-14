#  Copyright (c) 2021 Piruin P.

from odoo import fields, models


class ServiceRequest(models.Model):
    _name = "ni.service.request"
    _description = "Service Request"
    _inherit = ["ni.patient.res", "period.mixin", "mail.thread", "mail.activity.mixin"]

    service_id = fields.Many2one("ni.service", ondelete="restrict", required=True)
    priority = fields.Selection(
        [("0", "Routine"), ("1", "Urgent"), ("2", "ASAP"), ("3", "STAT")],
        default="0",
        required=True,
    )
    state = fields.Selection(
        [
            ("draft", "Request"),
            ("active", "In-Progress"),
            ("on-hold", "On-hold"),
            ("revoked", "Revoked"),
            ("completed", "Completed"),
            ("entered-in-error", "Error Entry"),
        ],
        default="draft",
        required=True,
    )
    requester_id = fields.Many2one(
        "res.partner", "Requester", default=lambda self: self.env.user.partner_id
    )
    instruction = fields.Text(help="Patient oriented instructions")
    approve_uid = fields.Many2one("res.users", "Approved by")
    approve_date = fields.Datetime("Approved on")

    def action_approve(self):
        self.write(
            {
                "state": "active",
                "approve_date": fields.Datetime.now(),
                "approve_uid": self.env.uid,
            }
        )
