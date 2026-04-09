from datetime import datetime, time, timezone

import pytz

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

    def _get_user_tz(self):
        tz_name = self.env.context.get("tz") or self.env.user.tz or "UTC"
        return pytz.timezone(tz_name)

    @api.depends("user_id", "start", "stop")
    def _compute_attendance_ids(self):
        tz = self._get_user_tz()

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

            # start: localize เป็น local 00:00 แล้วแปลงเป็น naive UTC
            start_of_first_day = tz.localize(datetime.combine(rec.start, time.min))
            query_start = start_of_first_day.astimezone(timezone.utc).replace(
                tzinfo=None
            )

            # stop: localize เป็น local 23:59:59 แล้วแปลงเป็น naive UTC
            end_of_last_day = tz.localize(datetime.combine(rec.stop, time.max))
            query_stop = end_of_last_day.astimezone(timezone.utc).replace(tzinfo=None)

            attendances = self.env["hr.attendance"].search(
                [
                    ("employee_id", "=", employee.id),
                    ("check_in", ">=", query_start),
                    ("check_in", "<=", query_stop),
                ]
            )

            rec.attendance_ids = attendances

            # ✅ แปลง check_in UTC → local date ก่อนนับวัน
            days = {
                att.check_in.replace(tzinfo=timezone.utc).astimezone(tz).date()
                for att in attendances
                if att.check_in
            }
            rec.attendance_days = len(days)

            total_hours = sum(att.worked_hours for att in attendances)
            rec.attendance_hours_total = total_hours
            rec.attendance_hours_avg = total_hours / len(days) if days else 0.0

    def action_view_attendance(self):
        self.ensure_one()

        if not self.employee_id:
            return {
                "type": "ir.actions.act_window_close",
            }

        return {
            "name": "Attendances",
            "type": "ir.actions.act_window",
            "res_model": "hr.attendance",
            "view_mode": "pivot,tree,form",
            "target": "current",
            "domain": [
                ("employee_id", "=", self.employee_id.id),
                ("check_in", ">=", self.start),
                ("check_in", "<=", self.stop),
            ],
            "context": dict(self.env.context),
        }

    @api.depends("attendance_ids")
    def _compute_attendance_days_count(self):
        tz = self._get_user_tz()
        for record in self:
            # ✅ แปลง check_in UTC → local date ก่อนนับ
            unique_days = {
                att.replace(tzinfo=timezone.utc).astimezone(tz).date()
                for att in record.attendance_ids.mapped("check_in")
                if att
            }
            record.attendance_days_count = len(unique_days)
