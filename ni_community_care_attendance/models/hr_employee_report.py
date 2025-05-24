from odoo import _, api, models


class EmployeeReport(models.Model):
    _name = "ni.employee.report"
    _description = "Employee Report"

    # @api.model
    # def get_employee_dashboard(self):
    #     user = self.env.user
    #
    #     employees = self.env["hr.employee"].search(
    #         [("city_ids", "in", user.employee_id.city_ids.ids)]
    #     )
    #     employee_ids = employees.ids
    #
    #     total_employees = len(employees)
    #     attended = employees.filtered(lambda e: e.attended_today)
    #     attended_count = len(attended)
    #
    #     # วันนี้
    #     today_start = datetime.combine(date.today(), datetime.min.time())
    #     today_end = datetime.combine(date.today(), datetime.max.time())
    #
    #     # หา user_ids ของพนักงาน
    #     user_ids = (
    #         self.env["res.users"].search([("employee_id", "in", employee_ids)]).ids
    #     )
    #
    #     # ดึงกิจกรรมวันนี้
    #     events_today = self.env["ni.service.event"].search(
    #         [
    #             ("user_id", "in", user_ids),
    #             ("stop", ">=", today_start),
    #             ("start", "<=", today_end),
    #         ]
    #     )
    #
    #     # นับจำนวนผู้สูงอายุที่ได้รับการดูแล (ไม่ซ้ำ)
    #     patient_ids_set = set()
    #     for event in events_today:
    #         patient_ids_set.update(event.plan_patient_ids.ids)
    #     cared_count = len(patient_ids_set)
    #
    #     res = {
    #         "attended_today": {
    #             "description": _("เข้างานวันนี้"),
    #             "amount": attended_count,
    #             "target": total_employees,
    #             "class": "text-success",
    #             "icon": "fa-check-circle",
    #         },
    #         "cared_today": {
    #             "description": _("ผู้สูงอายุที่ได้รับการดูแลในวันนี้"),
    #             "amount": cared_count,
    #             "target": 0,
    #             "class": "text-odoo",
    #             "icon": "fa-user",
    #         },
    #         "event_today": {
    #             "description": _("กิจกรรมดูแลผู้สูงอายุในวันนี้"),
    #             "amount": len(events_today),
    #             "target": 0,
    #             "class": "text-danger",
    #             "icon": "fa-calendar",
    #         },
    #     }
    #
    #     return res

    @api.model
    def get_employee_dashboard(self):
        user = self.env.user

        employees = self.env["hr.employee"].search(
            [("city_ids", "in", user.employee_id.city_ids.ids)]
        )
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
