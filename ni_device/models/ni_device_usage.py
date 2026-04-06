#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class DeviceUsage(models.Model):
    _name = "ni.device.usage"
    _description = "Device Usage"
    _order = "create_date desc"
    _inherit = "ni.identifier.mixin"

    device_id = fields.Many2one(
        "ni.device", required=True, index=True, ondelete="cascade"
    )

    definition_id = fields.Many2one(
        related="device_id.definition_id", store=True, index=True
    )

    state = fields.Selection(
        [
            ("in-progress", "Active"),
            ("suspended", "On Hold"),
            ("abort", "Stopped"),
            ("completed", "Completed"),
        ],
        "State",
        required=True,
        default="in-progress",
    )

    company_id = fields.Many2one(
        "res.company", index=True, default=lambda self: self.env.company
    )
    user_id = fields.Many2one("res.users", "User", default=lambda self: self.env.user)

    patient_id = fields.Many2one(
        "ni.patient",
        "Patient",
        index=True,
    )

    occurrence = fields.Datetime(
        required=True, default=lambda _: fields.Datetime.now(), index=True
    )

    res_model = fields.Selection(
        [
            ("ni.observation.sheet", "Observation Sheet"),
            ("ni.patient.smartcard", "Smartcard"),
        ],
        "Reference Model",
        required=True,
        index=True,
    )

    res_id = fields.Integer(index=True)

    res_name = fields.Char(
        string="Reference Name",
        compute="_compute_res_name",
        store=False,
    )

    def _compute_res_name(self):
        for rec in self:
            name = False
            if rec.res_model and rec.res_id:
                record = self.env[rec.res_model].browse(rec.res_id)
                if record.exists():
                    name = record.display_name
            rec.res_name = name

    def action_open_source(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": self.res_model,
            "res_id": self.res_id,
            "view_mode": "form",
            "target": "current",
        }

    def action_fetch_from_source(self):
        self.ensure_one()

        if not self.res_model or not self.res_id:
            return False

        record = self.env[self.res_model].browse(self.res_id)
        if not record.exists():
            return False

        # ใช้ logic เดียวกับ mixin
        vals = {}

        # device
        if hasattr(record, "device_id"):
            vals["device_id"] = record.device_id.id

        # patient
        if hasattr(record, "patient_id"):
            vals["patient_id"] = record.patient_id.id

        # user
        if hasattr(record, "user_id"):
            vals["user_id"] = record.user_id.id

        self.write(vals)
