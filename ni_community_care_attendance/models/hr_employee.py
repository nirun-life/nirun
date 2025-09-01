from odoo import api, fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    attended_today = fields.Boolean(
        string="เข้างานวันนี้", compute="_compute_attendance_summary"
    )

    days_attended_this_month = fields.Integer(
        string="เข้างานเดือนนี้", compute="_compute_attendance_summary"
    )
    care_days_this_month = fields.Integer(
        string="ดูแลผู้สูงอายุเดือนนี้", compute="_compute_care_days_this_month"
    )

    on_leave_today = fields.Boolean(
        string="On Leave Today", compute="_compute_on_leave_today", store=False
    )

    @api.depends("user_id")
    def _compute_on_leave_today(self):
        today = fields.Date.today()
        Leave = self.env["hr.leave"]
        # ดึง leave ทั้งหมดที่อนุมัติและครอบคลุมวันนี้ของพนักงานทั้งหมดใน self
        for emp in self:
            leave = Leave.search(
                [
                    ("employee_id", "=", emp.id),
                    ("request_date_from", "<=", today),
                    ("request_date_to", ">=", today),
                ],
                limit=1,
            )
            emp.on_leave_today = bool(leave)

    @api.depends("user_id")  # เพิ่ม fields ที่จะเปลี่ยน
    def _compute_attendance_summary(self):
        today = fields.Date.today()
        start_of_month = today.replace(day=1)
        for rec in self:
            attendances = self.env["hr.attendance"].search(
                [
                    ("employee_id", "=", rec.id),
                    ("check_in", ">=", start_of_month),
                    ("check_in", "<=", today),
                ]
            )
            rec.days_attended_this_month = len(
                {att.date() for att in attendances.mapped("check_in") if att}
            )
            rec.attended_today = any(
                att.check_in and att.check_in.date() == today for att in attendances
            )

    @api.depends("user_id")
    def _compute_care_days_this_month(self):
        today = fields.Date.today()
        start_of_month = today.replace(day=1)
        for rec in self:
            # ค้นหา event ที่ user_id ตรงกับ record นี้
            # และมีช่วงเวลา start-stop ซ้อนทับกับช่วงของ record นี้
            events = self.env["ni.service.event"].search(
                [
                    ("user_id", "=", rec.user_id.id),
                    (
                        "stop",
                        ">=",
                        start_of_month,
                    ),  # event ยังไม่จบก่อน start ของ record
                    ("start", "<=", today),  # event เริ่มไม่หลัง stop ของ record
                ],
                order="start desc",
            )

            # รวม patient_id ที่ไม่ซ้ำ
            patient_ids = set()
            for ev in events:
                patient_ids.update(ev.plan_patient_ids.ids)

            rec.care_days_this_month = len(patient_ids)
