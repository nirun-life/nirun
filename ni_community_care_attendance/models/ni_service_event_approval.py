from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ServiceEventApprovalAttendance(models.Model):
    _inherit = "ni.service.event.approval"

    attendance_ids = fields.One2many(
        comodel_name="hr.attendance",
        compute="_compute_attendance_ids",
        string="รายการเข้างาน",
    )

    attendance_days = fields.Integer(
        string="จำนวนวันที่เข้างาน",
        compute="_compute_attendance_ids",
    )
    attendance_days_count = fields.Integer(
        string="Attendance Days Count", compute="_compute_attendance_days_count"
    )

    attendance_hours_total = fields.Float(
        string="จำนวนชั่วโมงที่เข้างานทั้งหมด",
        compute="_compute_attendance_ids",
        store=True,
    )

    attendance_hours_avg = fields.Float(
        string="จำนวนชั่วโมงเฉลี่ยต่อวัน", compute="_compute_attendance_ids", store=True
    )

    @api.depends("user_id", "start", "stop")
    def _compute_attendance_ids(self):
        for rec in self:
            rec.attendance_ids = False
            rec.attendance_days = 0
            rec.attendance_hours_total = 0.0
            rec.attendance_hours_avg = 0.0

            if not rec.user_id or not rec.start or not rec.stop:
                continue

            employee = self.env["hr.employee"].search(
                [("user_id", "=", rec.user_id.id)], limit=1
            )

            if not employee:
                continue

            attendances = self.env["hr.attendance"].search(
                [
                    ("employee_id", "=", employee.id),
                    ("check_in", ">=", rec.start),
                    ("check_in", "<=", rec.stop),
                ]
            )

            rec.attendance_ids = attendances

            # วันที่ไม่ซ้ำที่เข้างาน
            days = {a.check_in.date() for a in attendances if a.check_in}
            rec.attendance_days = len(days)

            # ชั่วโมงรวม และเฉลี่ย
            total_hours = sum(att.worked_hours for att in attendances)
            rec.attendance_hours_total = total_hours
            rec.attendance_hours_avg = total_hours / len(days) if days else 0.0

    def action_view_attendance(self):
        self.ensure_one()
        # หา employee ที่สัมพันธ์กับ user_id
        employee = self.env["hr.employee"].search(
            [("user_id", "=", self.user_id.id)], limit=1
        )
        if not employee:
            return {
                "type": "ir.actions.act_window_close",
            }

        return {
            "name": "Attendances",
            "type": "ir.actions.act_window",
            "res_model": "hr.attendance",
            "view_mode": "tree,form",
            "target": "current",
            "domain": [
                ("employee_id", "=", employee.id),
                ("check_in", ">=", self.start),
                ("check_in", "<=", self.stop),
            ],
            "context": dict(self.env.context),
        }

    @api.depends("attendance_ids")
    def _compute_attendance_days_count(self):
        for record in self:
            # นับวันที่ไม่ซ้ำกันจาก attendance_ids
            unique_days = {
                att.date() for att in record.attendance_ids.mapped("check_in") if att
            }
            record.attendance_days_count = len(unique_days)

    @api.model
    def create_record_from_cron(self):
        """สร้าง record สำหรับผู้ใช้ทุกคน"""
        # เลื่อนเวลาไปเดือนก่อนหน้า
        today = fields.Date.today()
        prev_month = today - relativedelta(months=1)

        # วันแรกของเดือนก่อนหน้า
        start_date = prev_month.replace(day=1)

        # วันสุดท้ายของเดือนก่อนหน้า
        last_day = start_date + relativedelta(months=1, days=-1)

        # ดึง user ทั้งหมด (กรองได้ถ้าต้องการเฉพาะ group)
        group_user = self.env.ref("ni_patient.group_user")
        group_manager = self.env.ref("ni_patient.group_manager")
        group_admin = self.env.ref("ni_patient.group_admin")

        users = self.env["res.users"].search(
            [
                ("groups_id", "in", [group_user.id]),
                ("groups_id", "not in", [group_manager.id]),
                ("groups_id", "not in", [group_admin.id]),
            ]
        )

        for user in users:
            self.create({"start": start_date, "stop": last_day, "user_id": user.id})
