from odoo import _, api, models


class EmployeeReport(models.Model):
    _name = "ni.employee.report"
    _description = "Employee Report"

    @api.model
    def get_employee_dashboard(self):
        employees = self.env["hr.employee"].search([("my_area", "=", True)])
        total_employees = len(employees)

        # คนที่มาทำงาน
        attended = employees.filtered(lambda e: e.attended_today)
        attended_ids = set(attended.ids)

        # คนที่ลางาน (on_leave_today) ยกเว้นคนที่มาเข้างาน
        leave_employees = employees.filtered(
            lambda e: e.on_leave_today and e.id not in attended_ids
        )
        leave_count = len(leave_employees)

        # ขาดงาน = ทั้งหมด - เข้างาน - ลางาน
        absent_count = total_employees - len(attended) - leave_count
        if absent_count < 0:
            absent_count = 0

        res = {
            "attended_today": {
                "description": _("เข้างานวันนี้"),
                "amount": len(attended),
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

        return res
