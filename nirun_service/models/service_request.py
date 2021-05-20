#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class ServiceRequest(models.Model):
    _name = "ni.service.request"
    _description = "Service Request"
    _inherit = ["ni.patient.res", "period.mixin", "mail.thread", "mail.activity.mixin"]

    display_name = fields.Char(compute="_compute_display_name")
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

    @api.depends("service_id", "patient_id", "state")
    def _compute_display_name(self):
        diff = dict(show_patient=None, show_state=None)
        names = dict(self.with_context(**diff).name_get())
        for rec in self:
            rec.display_name = names.get(rec.id)

    def name_get(self):
        res = []
        for rec in self:
            name = rec._get_name()
            res.append((rec.id, name))
        return res

    def _get_name(self):
        self.ensure_one()
        rec = self
        name = "#{} - {}".format(rec.id, rec.service_id.name)
        if self._context.get("show_state"):
            name = "{} [{}]".format(name, rec._get_state_label())
        if self._context.get("show_patient"):
            name = "{}\n{}".format(name, rec.patient_id.name)
        return name

    def _get_state_label(self):
        self.ensure_one()
        return dict(self._fields["state"].selection).get(self.state)

    def action_approve(self):
        self.write(
            {
                "state": "active",
                "approve_date": fields.Datetime.now(),
                "approve_uid": self.env.uid,
            }
        )
