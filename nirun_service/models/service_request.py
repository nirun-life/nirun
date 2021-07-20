#  Copyright (c) 2021 Piruin P.

from odoo import api, fields, models


class ServiceRequest(models.Model):
    _name = "ni.service.request"
    _description = "Service Request"
    _inherit = ["ni.patient.res", "period.mixin", "mail.thread"]
    _order = "id DESC"

    patient_id = fields.Many2one(readonly=True, states={"draft": [("readonly", False)]})
    encounter_id = fields.Many2one(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    display_name = fields.Char(compute="_compute_display_name")
    service_id = fields.Many2one(
        "ni.service",
        ondelete="restrict",
        readonly=True,
        required=True,
        states={"draft": [("readonly", False)]},
    )
    category_ids = fields.Many2many(related="service_id.category_ids")
    priority = fields.Selection(
        [("0", "Routine"), ("1", "Urgent"), ("2", "ASAP"), ("3", "STAT")],
        default="0",
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Request"),
            ("active", "In-Progress"),
            ("on-hold", "On-hold"),
            ("revoked", "Revoked"),
            ("completed", "Completed"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    requester_id = fields.Many2one(
        "res.partner",
        "Requester",
        default=lambda self: self.env.user.partner_id,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    instruction = fields.Text(help="Patient oriented instructions")
    approve_uid = fields.Many2one("res.users", "Approved by", readonly=True)
    approve_date = fields.Datetime("Approved on", readonly=True)

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
        records = self.filtered(lambda rec: rec.state == "draft")
        records.write(
            {
                "state": "active",
                "approve_date": fields.Datetime.now(),
                "approve_uid": self.env.uid,
            }
        )

    def action_pause(self):
        records = self.filtered(lambda rec: rec.state == "active")
        records.write({"state": "on-hold"})

    def action_resume(self):
        records = self.filtered(lambda rec: rec.state == "on-hold")
        records.write({"state": "active"})

    def action_complete(self):
        records = self.filtered(lambda rec: rec.state == "active")
        records.write({"state": "completed"})

        today = fields.Date.today()
        records = records.filtered(
            lambda rec: not rec.period_end or rec.period_end > today
        )
        records.write({"period_end": today})

    def action_revoke(self):
        records = self.filtered(lambda rec: rec.state == "active")
        records.write({"state": "revoked"})

        today = fields.Date.today()
        records = records.filtered(
            lambda rec: not rec.period_end or rec.period_end > today
        )
        records.write({"period_end": today})
