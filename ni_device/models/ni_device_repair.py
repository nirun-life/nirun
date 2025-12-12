from odoo import fields, models


class DeviceRepairHistory(models.Model):
    _name = "ni.device.repair"
    _description = "Device Repair History"
    _rec_name = "identifier"
    _inherit = ["ni.identifier.mixin", "image.mixin"]

    device_id = fields.Many2one(
        "ni.device",
        string="Device",
        required=True,
        ondelete="cascade",
    )
    device_holder_emp_id = fields.Many2one(related="device_id.holder_employee_id")
    device_holder_id = fields.Many2one(related="device_id.holder_id")
    device_holder_name = fields.Char(related="device_id.holder_name")
    is_holder = fields.Boolean(related="device_id.is_holder")
    is_manager = fields.Boolean(related="device_id.is_manager")

    # Date the device was damaged (Requirement)
    damage_date = fields.Datetime(
        string="Damage Date",
        required=True,
        default=fields.Datetime.now,
    )

    # Currency (Required for Monetary Fields)
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id.id,
    )

    # Repair Cost
    repair_cost = fields.Monetary(
        string="Repair Cost",
        currency_field="currency_id",
    )

    # Repair Duration (Requirement)
    repair_duration = fields.Integer(
        string="Repair Duration (days)",
    )

    # Additional Details
    note = fields.Html(
        string="Additional Details",
    )

    # Repair Process Status
    state = fields.Selection(
        [
            ("damaged", "Damaged"),
            ("repairing", "Repairing"),
            ("completed", "Completed"),
        ],
        default="damaged",
        string="Status",
    )

    # Optional: Technician in charge
    technician_id = fields.Many2one(
        "res.partner",
        string="Technician",
        domain=[("is_company", "=", False)],
    )

    # Estimated Repair Duration (optional)
    estimated_duration = fields.Float(
        string="Estimated Duration",
    )

    # Estimated Repair Cost (optional)
    estimated_cost = fields.Monetary(
        string="Estimated Repair Cost",
        currency_field="currency_id",
    )

    def action_confirm_repair(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "ยืนยันผลการซ่อม",
            "res_model": "ni.device.repair",
            "view_mode": "form",
            "view_id": self.env.ref("ni_device.ni_device_repair_view_form").id,
            "res_id": self.id,  # <<< สำคัญ: เปิด record ปัจจุบัน
            "target": "new",  # <<< เปิดใน wizard popup
        }
