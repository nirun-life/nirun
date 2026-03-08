import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Device(models.Model):
    _name = "ni.device"
    _description = "Device Registry"
    _inherit = ["ni.identifier.mixin", "image.mixin", "mail.thread", "ni.holder.mixin"]
    _rec_name = "name"
    _order = "name"

    name = fields.Char(string="Device Name", required=True)
    identifier = fields.Char("Identifier", readonly=True)

    manufacturer_id = fields.Many2one(
        "res.partner",
        string="Manufacturer",
        domain="[('is_company', '=', True)]",
        store=True,
    )
    manufacture_date = fields.Date("Manufacturer Date")
    serial_number = fields.Char(
        "Serial Number",
        required=True,
        help="If no serial number is available, you may enter - instead.",
    )
    model_number = fields.Char("Model")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    price = fields.Monetary(
        "Price",
        currency_field="currency_id",
    )
    barcode = fields.Char(string="Barcode", related="identifier")

    type_ids = fields.Many2many(
        "ni.device.type",
        string="Device Types",
        help="Examples: Blood Pressure Monitor, Weighing Scale, Thermometer",
        required=True,
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

    observation_type_ids = fields.Many2many(
        "ni.observation.type",
        string="Supported Observation Type",
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

    usage_log_ids = fields.One2many(
        "ni.device.usage.log",
        "device_id",
        string="Device Usage Logs",
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

    received_date = fields.Date(
        string="Received Date",
        help="The date the device was received and registered in the system.",
        required=True,
    )
    disposed_date = fields.Datetime(
        string="Disposed Date",
        store=True,
        readonly=True,
    )

    holder_history_count = fields.Integer(compute="_compute_holder_history_count")
    request_count = fields.Integer(compute="_compute_request_count")
    repair_count = fields.Integer(compute="_compute_repair_count")
    usage_log_count = fields.Integer(compute="_compute_usage_log_count")

    can_request_as_holder = fields.Boolean(
        compute="_compute_can_request_as_holder",
        store=False,
    )

    not_repairable = fields.Boolean(
        compute="_compute_is_not_repairable",
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

    @api.depends("usage_log_ids")
    def _compute_usage_log_count(self):
        for rec in self:
            rec.usage_log_count = len(rec.usage_log_ids)

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
                lambda r: r.state in ("damaged", "repairing", "not_repairable")
            )

            # ถ้ามีหลายตัว → เอาตัวล่าสุดจาก create_date
            if current:
                rec.active_repair_id = current.sorted("create_date")[-1]
            else:
                rec.active_repair_id = False

    @api.depends(
        "state", "is_holder", "is_manager", "pending_request_id", "active_repair_id"
    )
    def _compute_can_request_as_holder(self):
        for rec in self:
            rec.can_request_as_holder = (
                rec.state == "in_use"
                and (rec.is_holder or rec.is_manager)
                and not rec.pending_request_id
                and not rec.active_repair_id
            )

    @api.depends("state", "active_repair_id", "active_repair_id.repair_result")
    def _compute_is_not_repairable(self):
        for rec in self:
            rec.not_repairable = (
                rec.state != "disposed"
                and rec.active_repair_id
                and rec.active_repair_id.repair_result == "not_repairable"
            )

    def action_repair(self):
        self.ensure_one()
        # เซ็ตสถานะอุปกรณ์ให้เป็น damaged

        return {
            "type": "ir.actions.act_window",
            "name": "Report Device Repair",
            "res_model": "ni.device.repair",
            "view_mode": "form",
            "view_id": self.env.ref(
                "ni_device.ni_device_repair_view_form_wizard_create"
            ).id,
            "target": "new",  # เปิด popup
            "context": {
                "default_device_id": self.id,
                "default_damage_date": fields.Datetime.now(),
            },
        }

    def action_request_hold(self):
        return self._action_open_request_wizard(
            request_type="request_hold",
            action_name="Request Device Holding",
            employee_source="current_user",
            include_new_holder=True,
        )

    def action_request_return(self):
        return self._action_open_request_wizard(
            request_type="request_return",
            action_name="Return Device",
            employee_source="device_holder",
        )

    def action_request_transfer(self):
        return self._action_open_request_wizard(
            request_type="request_transfer",
            action_name="Transfer Holder",
            employee_source="device_holder",
        )

    def action_request_dispose(self):
        return self._action_open_request_wizard(
            request_type="request_dispose",
            action_name="Device Disposal",
            employee_source="device_holder",
        )

    def _action_open_request_wizard(
        self,
        *,
        request_type,
        action_name,
        employee_source="current_user",  # current_user | device_holder
        include_new_holder=False,
    ):
        self.ensure_one()

        if employee_source == "device_holder":
            employee = self.holder_employee_id
        else:
            employee = self.env.user.employee_id

        partner = (
            (employee.user_id.partner_id or employee.address_home_id)
            if employee
            else False
        )

        context = {
            "default_device_id": self.id,
            "default_request_type": request_type,
            "default_company_id": self.company_id.id,
            "default_holder_employee_id": employee.id if employee else False,
            "default_holder_partner_id": partner.id if partner else False,
        }

        if include_new_holder:
            context.update(
                {
                    "default_new_holder_employee_id": employee.id
                    if employee
                    else False,
                    "default_new_holder_partner_id": partner.id if partner else False,
                }
            )

        return {
            "type": "ir.actions.act_window",
            "name": action_name,
            "res_model": "ni.device.request",
            "view_mode": "form",
            "views": [
                (
                    self.env.ref("ni_device.ni_device_request_view_form_wizard").id,
                    "form",
                ),
            ],
            "target": "new",
            "context": context,
        }

    def action_open_label_layout(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Print Device Labels",
            "res_model": "ni.device.label.layout",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_device_id": self.id,
                "default_quantity": 1,
            },
        }

    def action_print_device_label(self):
        self.ensure_one()
        return self.env.ref("ni_device.action_report_device_label").report_action(self)
