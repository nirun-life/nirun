from datetime import datetime, timezone

import pytz

from odoo import _, api, models


class EmployeeReport(models.Model):
    _name = "ni.employee.report"
    _description = "Employee Report"

    @api.model
    def get_employee_dashboard(self):
        # ✅ ดึง tz จาก context ของ user
        tz_name = self.env.context.get("tz") or self.env.user.tz or "UTC"
        tz = pytz.timezone(tz_name)

        now_local = datetime.now(tz)
        today = now_local.date()

        # start_of_day ตาม local timezone แปลงกลับเป็น naive UTC สำหรับ query
        start_of_day_local = now_local.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        start_of_day_utc = start_of_day_local.astimezone(timezone.utc).replace(
            tzinfo=None
        )

        employees = self.env["hr.employee"].search([("my_area", "=", True)])
        total_employees = len(employees)
        emp_ids = employees.ids

        if not emp_ids:
            return {
                "attended_today": {
                    "description": _("เข้างานวันนี้"),
                    "amount": 0,
                    "target": 0,
                    "class": "text-success",
                    "icon": "fa-check-circle",
                },
                "absent_today": {
                    "description": _("ไม่เข้างานวันนี้"),
                    "amount": 0,
                    "target": 0,
                    "class": "text-danger",
                    "icon": "fa-times-circle",
                },
                "leave_today": {
                    "description": _("ลางานวันนี้"),
                    "amount": 0,
                    "target": 0,
                    "class": "text-warning",
                    "icon": "fa-plane",
                },
            }

        # ✅ Batch query: ดึง attendance วันนี้ของทุก employee พร้อมกัน (1 query)
        attendances = self.env["hr.attendance"].search(
            [
                ("employee_id", "in", emp_ids),
                ("check_in", ">=", start_of_day_utc),  # ✅ naive UTC
            ]
        )
        attended_ids = set(attendances.mapped("employee_id").ids)

        # ✅ Batch query: ดึง leave วันนี้ของทุก employee พร้อมกัน (1 query)
        leaves = self.env["hr.leave"].search(
            [
                ("employee_id", "in", emp_ids),
                ("request_date_from", "<=", today),
                ("request_date_to", ">=", today),
                ("state", "!=", "refuse"),
            ]
        )
        leave_ids = set(leaves.mapped("employee_id").ids) - attended_ids

        attended_count = len(attended_ids)
        leave_count = len(leave_ids)
        absent_count = max(0, total_employees - attended_count - leave_count)

        return {
            "attended_today": {
                "description": _("เข้างานวันนี้"),
                "amount": attended_count,
                "target": total_employees,
                "class": "text-success",
                "icon": "fa-check-circle",
            },
            "absent_today": {
                "description": _("ไม่เข้างานวันนี้"),
                "amount": absent_count,
                "target": total_employees,
                "class": "text-danger",
                "icon": "fa-times-circle",
            },
            "leave_today": {
                "description": _("ลางานวันนี้"),
                "amount": leave_count,
                "target": total_employees,
                "class": "text-warning",
                "icon": "fa-plane",
            },
        }
