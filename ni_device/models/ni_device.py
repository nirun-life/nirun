import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Device(models.Model):
    _name = "ni.device"
    _description = "Device Registry"
    _inherit = ["ni.identifier.mixin", "image.mixin", "mail.thread"]
    _rec_name = "name"
    _order = "name"

    name = fields.Char(string="Device Name")
    identifier = fields.Char("Identifier", readonly=True)

    manufacturer_id = fields.Many2one(
        "res.partner",
        string="Manufacturer",
        domain="[('is_company', '=', True)]",
        store=True,
    )
    manufacture_date = fields.Date("Manufacturer Date")
    serial_number = fields.Char("Serial Number")
    model_number = fields.Char("Model")
    price = fields.Float("Price")
    type_ids = fields.Many2many(
        "ni.device.type",
        string="Device Types",
        help="Examples: Blood Pressure Monitor, Weighing Scale, Thermometer",
    )
    availability_status = fields.Selection(
        [
            ("available", "Available"),
            ("damaged", "Damaged"),
            ("disposed", "Disposed"),
            ("lost", "Lost"),
        ],
        default="available",
        string="Availability Status",
    )
    metric_ids = fields.Many2many(
        "ni.device.metric",
        string="Supported Health Metrics",
        help="e.g., Blood Pressure, Temperature, Weight",
    )
    state = fields.Selection(
        [
            ("available", "Available"),
            ("pending", "Pending"),
            ("in_use", "In Use"),
            ("disposed", "Disposed"),
        ],
        default="available",
        string="Holding Status",
        store=True,
    )
    company_id = fields.Many2one("res.company", string="Company", store=True)

    holder_id = fields.Many2one(
        "res.partner",
        string="Current Holder",
        store=True,
        help="The caregiver or department that holds the device during this period.",
    )

    holder_history_ids = fields.One2many(
        "ni.device.holder",
        "device_id",
        string="Holder History",
    )

    request_ids = fields.One2many(
        "ni.device.request",
        "device_id",
        string="Holding Change Request",
    )

    pending_request_id = fields.Many2one(
        "ni.device.request",
        string="Pending Request",
        store=True,
    )

    repair_ids = fields.One2many(
        "ni.device.repair",
        "device_id",
        string="Repair History",
    )

    is_holder = fields.Boolean(
        compute="_compute_is_holder", store=False, search="_search_is_holder"
    )
    is_manager = fields.Boolean(compute="_compute_is_manager", store=False)

    holder_history_count = fields.Integer(compute="_compute_holder_history_count")
    request_count = fields.Integer(compute="_compute_request_count")
    repair_count = fields.Integer(compute="_compute_repair_count")

    @api.depends("holder_history_ids")
    def _compute_holder_history_count(self):
        for rec in self:
            rec.holder_history_count = len(rec.holder_history_ids)

    @api.depends("request_ids")
    def _compute_request_count(self):
        for rec in self:
            rec.request_count = len(rec.request_ids)

    @api.depends("repair_ids")
    def _compute_repair_count(self):
        for rec in self:
            rec.repair_count = len(rec.repair_ids)

    @api.depends("holder_id", "holder_id.user_id")
    def _compute_is_holder(self):
        current_user = self.env.user
        current_partner = current_user.partner_id
        for rec in self:
            rec.is_holder = False
            if not rec.holder_id:
                continue
            # ครอบคลุมทั้งกรณี partner ถูกผูกกับ user และกรณี partner ตรงกับ user's partner
            if rec.holder_id.user_id and rec.holder_id.user_id == current_user:
                rec.is_holder = True
            elif rec.holder_id == current_partner:
                rec.is_holder = True
            else:
                rec.is_holder = False

    def _search_is_holder(self, operator, value):
        user = self.env.user
        partner_ids = [user.partner_id.id] + self.env["res.partner"].search(
            [("user_id", "=", user.id)]
        ).ids

        if value:  # is_holder = True
            return [("holder_id", "in", partner_ids)]
        else:  # is_holder = False
            return [
                "|",
                ("holder_id", "not in", partner_ids),
                ("holder_id", "=", False),
            ]

    @api.depends()
    def _compute_is_manager(self):
        user = self.env.user
        for rec in self:
            rec.is_manager = user.has_group("ni_patient.group_manager")

    def action_request_hold(self):
        """เปิด wizard ni.device.request แบบ form view"""
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Request Device Holding",
            "res_model": "ni.device.request",
            "view_mode": "form",
            "views": [
                (
                    self.env.ref("ni_device.ni_device_request_view_form_wizard").id,
                    "form",
                ),
            ],
            "target": "new",  # เปิดเป็น popup modal
            "context": {
                "default_device_id": self.id,
                "default_request_type": "request_hold",
                "default_holder_id": self.env.user.partner_id.id,
            },
        }

    def action_request_return(self):
        """เปิด wizard ni.device.request แบบ form view"""
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Return Device",
            "res_model": "ni.device.request",
            "view_mode": "form",
            "views": [
                (
                    self.env.ref("ni_device.ni_device_request_view_form_wizard").id,
                    "form",
                ),
            ],
            "target": "new",  # เปิดเป็น popup modal
            "context": {
                "default_device_id": self.id,
                "default_request_type": "request_return",
                "default_holder_id": self.holder_id.id if self.holder_id else False,
            },
        }

    def action_request_transfer(self):
        """เปิด wizard ni.device.request แบบ form view"""
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Transfer Holder",
            "res_model": "ni.device.request",
            "view_mode": "form",
            "views": [
                (
                    self.env.ref("ni_device.ni_device_request_view_form_wizard").id,
                    "form",
                ),
            ],
            "target": "new",  # เปิดเป็น popup modal
            "context": {
                "default_device_id": self.id,
                "default_request_type": "request_transfer",
                "default_holder_id": self.holder_id.id if self.holder_id else False,
                "show_new_holder": True,
            },
        }

    def action_request_dispose(self):
        """เปิด wizard ni.device.request แบบ form view"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Device Disposal",
            "res_model": "ni.device.request",
            "view_mode": "form",
            "views": [
                (
                    self.env.ref("ni_device.ni_device_request_view_form_wizard").id,
                    "form",
                ),
            ],
            "target": "new",  # เปิดเป็น popup modal
            "context": {
                "default_device_id": self.id,
                "default_request_type": "request_dispose",
                "default_holder_id": self.holder_id.id if self.holder_id else False,
            },
        }

    def action_repair(self):
        self.ensure_one()

        # เซ็ตสถานะอุปกรณ์ให้เป็น damaged
        self.availability_status = "damaged"

        return {
            "type": "ir.actions.act_window",
            "name": "Report Device Repair",
            "res_model": "ni.device.repair",
            "view_mode": "form",
            "target": "new",  # เปิด popup
            "context": {
                "default_device_id": self.id,
                "default_damage_date": fields.Datetime.now(),
            },
        }
