from datetime import timedelta

from odoo import fields, models
from odoo.exceptions import UserError


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    def write(self, vals):
        # ดึงค่าจาก system parameter (default 5 นาที)
        min_minutes = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("hr_attendance.min_checkout_minutes", 5)
        )
        min_duration = timedelta(minutes=min_minutes)

        if "check_out" in vals:
            for rec in self:
                if rec.check_in and not rec.check_out:
                    check_out_time = fields.Datetime.to_datetime(vals["check_out"])
                    if check_out_time - rec.check_in < min_duration:
                        raise UserError(
                            f"ไม่สามารถบันทึกเวลาออกงานภายใน {min_minutes} นาที หลังจากเช็คอิน"
                        )
        return super().write(vals)
