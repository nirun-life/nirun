import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Device(models.Model):
    _name = "ni.device"
    _description = "Device Registry"
    _inherit = ["ni.identifier.mixin", "image.mixin", "mail.thread", "ni.holder.mixin"]
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
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company.id,
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
        compute="_compute_pending_request",
        store=True,
    )

    active_repair_id = fields.Many2one(
        "ni.device.repair",
        string="Active Repair",
        compute="_compute_active_repair",
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

    can_request_as_holder = fields.Boolean(
        compute="_compute_can_request_as_holder",
        store=False,
    )

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

    @api.depends("request_ids", "request_ids.state")
    def _compute_pending_request(self):
        for rec in self:
            # หา request ที่ยัง pending
            pending = rec.request_ids.filtered(lambda r: r.state in ("pending"))

            # ถ้ามีหลายตัว → เอาตัวล่าสุดจาก create_date
            if pending:
                rec.pending_request_id = pending.sorted("create_date")[-1]
            else:
                rec.pending_request_id = False

    @api.depends("repair_ids", "repair_ids.state")
    def _compute_active_repair(self):
        for rec in self:
            # หา repair ที่ยัง
            current = rec.repair_ids.filtered(
                lambda r: r.state in ("damaged", "repairing")
            )

            # ถ้ามีหลายตัว → เอาตัวล่าสุดจาก create_date
            if current:
                rec.active_repair_id = current.sorted("create_date")[-1]
            else:
                rec.active_repair_id = False

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

    @api.depends("state", "is_holder", "is_manager", "pending_request_id")
    def _compute_can_request_as_holder(self):
        for rec in self:
            rec.can_request_as_holder = (
                rec.state == "in_use"
                and (rec.is_holder or rec.is_manager)
                and not rec.pending_request_id
                and not rec.active_repair_id
            )

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
                "default_company_id": self.company_id.id,
                "default_holder_employee_id": self.env.user.employee_id.id
                if self.env.user.employee_id
                else False,
                "default_new_holder_employee_id": self.env.user.employee_id.id
                if self.env.user.employee_id
                else False,
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
                "default_company_id": self.company_id.id,
                "default_holder_employee_id": self.env.user.employee_id.id
                if self.env.user.employee_id
                else False,
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
                "default_company_id": self.company_id.id,
                "default_holder_employee_id": self.env.user.employee_id.id
                if self.env.user.employee_id
                else False,
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
                "default_company_id": self.company_id.id,
                "default_holder_employee_id": self.env.user.employee_id.id
                if self.env.user.employee_id
                else False,
            },
        }

    def action_repair(self):
        self.ensure_one()
        # เซ็ตสถานะอุปกรณ์ให้เป็น damaged

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
