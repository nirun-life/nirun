from datetime import datetime, timezone

import pytz

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

    def _get_local_today(self):
        """คืนค่า date ของวันนี้ตาม timezone ของ user"""
        tz_name = self.env.context.get("tz") or self.env.user.tz or "UTC"
        tz = pytz.timezone(tz_name)
        return datetime.now(tz).date()

    @api.depends("user_id")
    def _compute_on_leave_today(self):
        today = self._get_local_today()
        Leave = self.env["hr.leave"]
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

    @api.depends("user_id")
    def _compute_attendance_summary(self):
        tz_name = self.env.context.get("tz") or self.env.user.tz or "UTC"
        tz = pytz.timezone(tz_name)

        now_local = datetime.now(tz)
        today = now_local.date()

        # แปลง start_of_month เป็น naive UTC สำหรับ query
        start_of_month_utc = (
            tz.localize(datetime(today.year, today.month, 1))
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

        for rec in self:
            attendances = self.env["hr.attendance"].search(
                [
                    ("employee_id", "=", rec.id),
                    ("check_in", ">=", start_of_month_utc),
                ]
            )

            # แปลง check_in UTC → local date ก่อนเทียบ
            local_dates = {
                att.check_in.replace(tzinfo=timezone.utc).astimezone(tz).date()
                for att in attendances
                if att.check_in
            }

            rec.days_attended_this_month = len(local_dates)
            rec.attended_today = today in local_dates

    @api.depends("user_id")
    def _compute_care_days_this_month(self):
        tz_name = self.env.context.get("tz") or self.env.user.tz or "UTC"
        tz = pytz.timezone(tz_name)

        now_local = datetime.now(tz)
        today = now_local.date()

        # แปลง start_of_month เป็น naive UTC สำหรับ query
        start_of_month_utc = (
            tz.localize(datetime(today.year, today.month, 1))
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )
        today_utc_end = (
            now_local.replace(hour=23, minute=59, second=59)
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )

        for rec in self:
            events = self.env["ni.service.event"].search(
                [
                    ("user_id", "=", rec.user_id.id),
                    ("stop", ">=", start_of_month_utc),
                    ("start", "<=", today_utc_end),
                ],
                order="start desc",
            )

            patient_ids = set()
            for ev in events:
                patient_ids.update(ev.plan_patient_ids.ids)

            rec.care_days_this_month = len(patient_ids)
