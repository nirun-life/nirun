#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    device_search = fields.Char(
        string="Device",
        search="_search_device",
    )

    def _search_device(self, operator, value):
        if not value:
            return []

        domain = [
            "|",
            "|",
            ("name", "ilike", value),
            ("serial_number", "ilike", value),
            ("identifier", "ilike", value),
        ]

        devices = self.env["ni.device"].search(domain)
        employee_ids = devices.mapped("holder_employee_id").ids

        if not employee_ids:
            return [("id", "=", 0)]

        return [("id", "in", employee_ids)]


class Employee(models.Model):
    _inherit = "hr.employee"

    device_ids = fields.One2many(
        "ni.device",
        "holder_employee_id",
        compute="_compute_device_and_holder",
        string="Devices",
        store=True,
    )

    holder_ids = fields.One2many(
        "ni.device.holder",
        compute="_compute_device_and_holder",
        string="Device Holders",
        store=False,
    )

    device_count = fields.Integer(
        compute="_compute_device_and_holder",
        string="Device Count",
    )

    holder_count = fields.Integer(
        compute="_compute_device_and_holder",
        string="Holder Count",
    )

    device_search = fields.Char(
        string="Device",
        search="_search_device",
    )

    def _search_device(self, operator, value):
        if not value:
            return []

        # รองรับ operator ทุกแบบ
        domain = [
            "|",
            "|",
            ("name", "ilike", value),
            ("serial_number", "ilike", value),
            ("identifier", "ilike", value),
        ]

        devices = self.env["ni.device"].search(domain)
        employee_ids = devices.mapped("holder_employee_id").ids

        # กัน case ไม่เจอ device เลย
        if not employee_ids:
            return [("id", "=", 0)]

        return [("id", "in", employee_ids)]

    def _compute_device_and_holder(self):
        Device = self.env["ni.device"]
        Holder = self.env["ni.device.holder"]

        for employee in self:
            devices = Device.search([("holder_employee_id", "=", employee.id)])
            holders = Holder.search([("holder_employee_id", "=", employee.id)])

            employee.device_ids = devices
            employee.holder_ids = holders
            employee.device_count = len(devices)
            employee.holder_count = len(holders)

    def action_view_devices(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Devices",
            "res_model": "ni.device",
            "view_mode": "tree,form",
            "domain": [("holder_employee_id", "=", self.id)],
            "context": {"default_holder_employee_id": self.id},
        }

    def action_view_device_holders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Device Holders",
            "res_model": "ni.device.holder",
            "view_mode": "tree,form",
            "domain": [("holder_employee_id", "=", self.id)],
            "context": {"default_holder_employee_id": self.id},
        }
