# Copyright 2025
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _attendance_action_change(self):
        """Override: ก่อน super() → รู้ state ปัจจุบัน (ก่อนสลับ)
        จึงใช้ attendance_state ก่อน super() เพื่อตัดสินว่ากำลังทำอะไร
        - ถ้า checked_in  → กำลังจะ check-out → บันทึก check_out area
        - ถ้า checked_out → กำลังจะ check-in  → บันทึก check_in area
        """
        latitude = self.env.context.get("latitude", False)
        longitude = self.env.context.get("longitude", False)

        # อ่าน state ก่อน super() (ก่อนสลับ)
        action_is_check_in = self.attendance_state == "checked_out"

        attendance = super()._attendance_action_change()

        if latitude and longitude and attendance:
            try:
                if action_is_check_in:
                    area_info = attendance.set_check_in_area(latitude, longitude)
                    _logger.info(
                        "Check-in area: %s | status: %s",
                        area_info.get("area_name"),
                        area_info.get("status"),
                    )
                else:
                    area_info = attendance.set_check_out_area(latitude, longitude)
                    _logger.info(
                        "Check-out area: %s | status: %s",
                        area_info.get("area_name"),
                        area_info.get("status"),
                    )
            except Exception as e:
                _logger.warning("Area check error: %s", e)

        return attendance

    def check_attendance_area(self):
        """ตรวจสอบพื้นที่จาก context lat/lon โดยไม่ check-in/out จริง
        คืน {out_of_area, area_name, responsible_areas, action_type}
        ถ้า service=none หรือ geocode ล้มเหลว → คืน out_of_area=False (ปล่อยผ่าน)
        """
        self.ensure_one()
        latitude = self.env.context.get("latitude", False)
        longitude = self.env.context.get("longitude", False)

        if not latitude or not longitude:
            return {"out_of_area": False}

        action_type = (
            "check_in" if self.attendance_state == "checked_out" else "check_out"
        )

        # ตรวจสอบ service config ก่อน (ถ้า none → ปล่อยผ่านเลย)
        attendance = self.env["hr.attendance"].new({"employee_id": self.id})
        service, _ = attendance._get_geocode_service()
        if service == "none":
            return {"out_of_area": False}

        _, status, district, state, _ = attendance._compute_area_info(
            latitude, longitude
        )

        if status != "out_of_area":
            return {"out_of_area": False}

        responsible_areas = []
        if hasattr(self, "city_ids") and self.city_ids:
            for city in self.city_ids:
                responsible_areas.append(city.name or "")
        elif self.state_id:
            responsible_areas.append(self.state_id.name or "")
        responsible_text = ", ".join(a for a in responsible_areas if a) or "ไม่ระบุ"

        from .hr_attendance import HrAttendance

        area_name = HrAttendance._format_area_short(district, state)

        return {
            "out_of_area": True,
            "action_type": action_type,
            "area_name": area_name or "ไม่ทราบพื้นที่",
            "responsible_areas": responsible_text,
        }

    def save_attendance_note(self, note, action_type="check_in"):
        """บันทึก note ลง attendance ล่าสุด แยก check_in_note / check_out_note"""
        self.ensure_one()
        if not note:
            return False
        last = (
            self.env["hr.attendance"]
            .sudo()
            .search(
                [("employee_id", "=", self.id)],
                order="check_in desc",
                limit=1,
            )
        )
        if last:
            field = "check_in_note" if action_type == "check_in" else "check_out_note"
            last.sudo().write({field: note})
        return True
