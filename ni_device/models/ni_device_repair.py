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
    device_holder_partner_id = fields.Many2one(related="device_id.holder_partner_id")
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

    # Estimated Repair Duration (optional)
    estimated_duration = fields.Integer(
        string="Estimated Duration (days)",
    )

    # Estimated Repair Cost (optional)
    estimated_cost = fields.Monetary(
        string="Estimated Repair Cost",
        currency_field="currency_id",
    )

    # Additional Details
    note = fields.Html(
        string="Note",
    )

    # Additional Details
    repairing_note = fields.Html(
        string="Repairing Note",
    )

    # Repair Process Status
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("damaged", "Damaged"),
            ("repairing", "Repairing"),
            ("completed", "Completed"),
            ("not_repairable", "Not Repairable"),
        ],
        default="draft",
        string="Status",
    )

    repair_result = fields.Selection(
        [
            ("repaired", "Ready for Use"),
            ("repaired_limited", "Repaired with Limitations"),
            ("not_repairable", "Not Repairable"),
        ],
        default="repaired",
        string="Repair Result",
    )

    # Optional: Technician in charge
    technician_id = fields.Many2one(
        "res.partner",
        string="Technician",
        domain=[("is_company", "=", False)],
    )

    can_action_as_holder = fields.Boolean(
        compute="_compute_can_action_as_holder",
        store=False,
    )

    def _compute_can_action_as_holder(self):
        for rec in self:
            rec.can_action_as_holder = rec.is_holder or rec.is_manager

    def action_submit(self):
        for rec in self.sudo():  # ← สำคัญ!
            rec.state = "damaged"
            rec.device_id.availability_status = "damaged"

    def action_repair_result(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Repair Result",  # <<< ยืนยันผลการซ่อม
            "res_model": "ni.device.repair",
            "res_id": self.id,  # <<< record เดิม
            "view_mode": "form",
            "view_id": self.env.ref(
                "ni_device.ni_device_repair_view_form_wizard_confirm"
            ).id,
            "target": "new",
            "context": {
                "state_action": "repair_result",
            },
        }

    def action_begin_repair(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Begin Repair",  # <<< ดำเนินการซ่อม
            "res_model": "ni.device.repair",
            "res_id": self.id,  # <<< record เดิม
            "view_mode": "form",
            "view_id": self.env.ref(
                "ni_device.ni_device_repair_view_form_wizard_confirm"
            ).id,
            "target": "new",
            "context": {
                "state_action": "repairing",
            },
        }

    def action_confirm(self):
        for rec in self.sudo():
            state_action = rec.env.context.get("state_action")

            # -----------------------
            # 1) ดำเนินการซ่อม
            # -----------------------
            if state_action == "repairing":
                rec.state = "repairing"

            # -----------------------
            # 2) ยืนยันผลการซ่อม
            # -----------------------
            elif state_action == "repair_result":
                if rec.repair_result == "not_repairable":
                    rec.state = "not_repairable"
                    rec.device_id.availability_status = "damaged"
                else:
                    rec.state = "completed"
                    rec.device_id.availability_status = "available"
