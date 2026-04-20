# Copyright 2025
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

AREA_STATUS = [
    ("in_area", "อยู่ในพื้นที่รับผิดชอบ"),
    ("out_of_area", "นอกพื้นที่รับผิดชอบ"),
    ("unknown", "ไม่สามารถระบุพื้นที่"),
]


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    employee_city_ids = fields.Many2many(
        related="employee_id.city_ids",
        string="พื้นที่รับผิดชอบ",
        readonly=True,
    )

    # ---- stored fields (เขียนจาก geocode) ----
    check_in_area_raw = fields.Char(
        string="[Dev] Check-in Address Raw",
        readonly=True,
        groups="base.group_no_one",
    )
    check_in_district = fields.Char(
        string="[Dev] Check-in District",
        readonly=True,
    )
    check_in_state_name = fields.Char(
        string="[Dev] Check-in State",
        readonly=True,
    )
    check_in_area_status = fields.Selection(
        selection=AREA_STATUS,
        string="สถานะพื้นที่เช็คอิน",
        readonly=True,
        default="unknown",
    )

    check_out_area_raw = fields.Char(
        string="[Dev] Check-out Address Raw",
        readonly=True,
        groups="base.group_no_one",
    )
    check_out_district = fields.Char(
        string="[Dev] Check-out District",
        readonly=True,
    )
    check_out_state_name = fields.Char(
        string="[Dev] Check-out State",
        readonly=True,
    )
    check_out_area_status = fields.Selection(
        selection=AREA_STATUS,
        string="สถานะพื้นที่เช็คเอาท์",
        readonly=True,
        default="unknown",
    )

    # ---- หมายเหตุนอกพื้นที่ ----
    check_in_note = fields.Text(string="หมายเหตุเช็คอิน")
    check_out_note = fields.Text(string="หมายเหตุเช็คเอาท์")

    # ---- compute fields สำหรับแสดง อ.xxx จ.yyy ----
    check_in_area_name = fields.Char(
        string="พื้นที่เช็คอิน",
        compute="_compute_area_display_names",
    )
    check_out_area_name = fields.Char(
        string="พื้นที่เช็คเอาท์",
        compute="_compute_area_display_names",
    )

    @api.depends(
        "check_in_district",
        "check_in_state_name",
        "check_out_district",
        "check_out_state_name",
    )
    def _compute_area_display_names(self):
        for rec in self:
            rec.check_in_area_name = self._format_area_short(
                rec.check_in_district, rec.check_in_state_name
            )
            rec.check_out_area_name = self._format_area_short(
                rec.check_out_district, rec.check_out_state_name
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_geocode_service(self):
        """อ่าน config จาก company"""
        company = self.env.company
        return (
            getattr(company, "attendance_geocode_service", "nominatim") or "nominatim",
            getattr(company, "attendance_longdo_api_key", "") or "",
        )

    def _reverse_geocode(self, lat, lon):
        """Reverse geocode ตาม service ที่ config ไว้ใน company
        ถ้า service=none หรือ error → return None (ปล่อยผ่าน)
        """
        if not lat or not lon:
            return None
        service, api_key = self._get_geocode_service()
        if service == "none":
            return None
        if service == "longdo":
            return self._reverse_geocode_longdo(lat, lon, api_key)
        return self._reverse_geocode_nominatim(lat, lon)

    def _reverse_geocode_nominatim(self, lat, lon):
        try:
            resp = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": lat,
                    "lon": lon,
                    "format": "json",
                    "addressdetails": 1,
                    "accept-language": "th",
                },
                headers={"User-Agent": "OdooHrAttendanceAreaCheck/1.0"},
                timeout=8,
            )
            if resp.status_code != 200:
                _logger.info("Nominatim HTTP %s — skipped", resp.status_code)
                return None
            data = resp.json()
            address = data.get("address", {})
            # Nominatim Thailand: province=จังหวัด, county=อำเภอ, city_district=ตำบล
            return {
                "state": address.get("province") or address.get("state") or "",
                "district": address.get("county")
                or address.get("city_district")
                or address.get("town")
                or "",
                "subdistrict": address.get("city_district")
                or address.get("suburb")
                or address.get("quarter")
                or "",
                "raw_address": data.get("display_name", ""),
            }
        except Exception as e:
            _logger.warning("Nominatim error: %s", e)
        return None

    def _reverse_geocode_longdo(self, lat, lon, api_key):
        if not api_key:
            _logger.warning("Longdo API key not configured")
            return None
        try:
            resp = requests.get(
                "https://api.longdo.com/map/services/address",
                params={"lon": lon, "lat": lat, "noelevation": 1, "key": api_key},
                timeout=8,
            )
            if resp.status_code != 200:
                _logger.info("Longdo HTTP %s — skipped", resp.status_code)
                return None
            data = resp.json()
            # Longdo response: district=อำเภอ, subdistrict=ตำบล, province=จังหวัด
            province = data.get("province", "")
            district = data.get("district", "")
            subdistrict = data.get("subdistrict", "")
            # Longdo ส่ง "กรุงเทพมหานคร" แทน "จังหวัดกรุงเทพมหานคร"
            parts = [p for p in [subdistrict, district, province] if p]
            return {
                "state": province,
                "district": district,
                "subdistrict": subdistrict,
                "raw_address": " ".join(parts),
            }
        except Exception as e:
            _logger.warning("Longdo error: %s", e)
        return None

    def _get_employee_city_ids(self):
        employee = self.employee_id
        if employee and hasattr(employee, "city_ids") and employee.city_ids:
            return employee.city_ids
        return self.env["res.city"].browse()

    def _get_employee_responsible_state(self):
        employee = self.employee_id
        if employee and employee.state_id:
            return employee.state_id.name
        return None

    @staticmethod
    def _normalize_name(name):
        """ตัด จ./จังหวัด/อ./อำเภอ/เขต นำหน้า แล้ว strip+lower"""
        if not name:
            return ""
        n = name.strip()
        for prefix in ("จังหวัด", "จ.", "อำเภอ", "อ.", "เขต"):
            if n.startswith(prefix):
                n = n[len(prefix) :]
                break
        return n.strip().lower()

    @staticmethod
    def _strip_prefix(name, prefixes):
        n = name.strip()
        for p in prefixes:
            if n.startswith(p):
                return n[len(p) :].strip()
        return n

    @staticmethod
    def _format_area_short(district, state):
        """แสดง อ.บางบัวทอง จ.นนทบุรี"""
        parts = []
        if district:
            d = HrAttendance._strip_prefix(district, ("อำเภอ", "เขต", "อ."))
            if d:
                parts.append(f"อ.{d}")
        if state:
            s = HrAttendance._strip_prefix(state, ("จังหวัด", "จ."))
            if s:
                parts.append(f"จ.{s}")
        return " ".join(parts) if parts else ""

    def _check_area_match(self, geo_district, geo_state, geo_subdistrict=""):
        """เช็คว่าพื้นที่ตรงกับ city_ids ของพนักงาน fallback: state_id"""
        city_ids = self._get_employee_city_ids()
        geo_district_norm = self._normalize_name(geo_district)
        geo_subdistrict_norm = self._normalize_name(geo_subdistrict)
        geo_state_norm = self._normalize_name(geo_state)

        if city_ids:
            for city in city_ids:
                city_state_norm = self._normalize_name(
                    city.state_id.name if city.state_id else ""
                )
                if (
                    city_state_norm
                    and geo_state_norm
                    and city_state_norm != geo_state_norm
                ):
                    continue
                city_name_norm = self._normalize_name(city.name or "")
                if geo_district_norm and city_name_norm:
                    if (
                        geo_district_norm in city_name_norm
                        or city_name_norm in geo_district_norm
                    ):
                        return True
                if not geo_district_norm and geo_subdistrict_norm and city_name_norm:
                    if (
                        geo_subdistrict_norm in city_name_norm
                        or city_name_norm in geo_subdistrict_norm
                    ):
                        return True
                if not city.name and city_state_norm == geo_state_norm:
                    return True
            return False

        employee_state = self._get_employee_responsible_state()
        if not employee_state:
            return True
        return self._normalize_name(geo_state) == self._normalize_name(employee_state)

    def _compute_area_info(self, lat, lon):
        """คืน (area_short, status, district, state, raw) — ถ้า geocode ล้มเหลว ปล่อยผ่าน"""
        geo = self._reverse_geocode(lat, lon)
        if not geo:
            return ("", "unknown", "", "", "")

        district = geo["district"]
        subdistrict = geo["subdistrict"]
        state = geo["state"]
        raw = geo["raw_address"]

        has_config = bool(
            self._get_employee_city_ids() or self._get_employee_responsible_state()
        )
        if not has_config or self._check_area_match(district, state, subdistrict):
            status = "in_area"
        else:
            status = "out_of_area"

        return (self._format_area_short(district, state), status, district, state, raw)

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def set_check_in_area(self, lat, lon):
        _, status, district, state, raw = self._compute_area_info(lat, lon)
        self.sudo().write(
            {
                "check_in_area_raw": raw,
                "check_in_district": district,
                "check_in_state_name": state,
                "check_in_area_status": status,
            }
        )
        return {
            "status": status,
            "employee_state": self._get_employee_responsible_state() or "",
        }

    def set_check_out_area(self, lat, lon):
        _, status, district, state, raw = self._compute_area_info(lat, lon)
        self.sudo().write(
            {
                "check_out_area_raw": raw,
                "check_out_district": district,
                "check_out_state_name": state,
                "check_out_area_status": status,
            }
        )
        return {"status": status}

    def action_refresh_area(self):
        self.ensure_one()
        lat_in = getattr(self, "check_in_latitude", None)
        lon_in = getattr(self, "check_in_longitude", None)
        if lat_in and lon_in:
            _, status, district, state, raw = self._compute_area_info(lat_in, lon_in)
            self.sudo().write(
                {
                    "check_in_area_raw": raw,
                    "check_in_district": district,
                    "check_in_state_name": state,
                    "check_in_area_status": status,
                }
            )
        lat_out = getattr(self, "check_out_latitude", None)
        lon_out = getattr(self, "check_out_longitude", None)
        if lat_out and lon_out:
            _, status, district, state, raw = self._compute_area_info(lat_out, lon_out)
            self.sudo().write(
                {
                    "check_out_area_raw": raw,
                    "check_out_district": district,
                    "check_out_state_name": state,
                    "check_out_area_status": status,
                }
            )
        return False

    def action_open_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.attendance",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
            "flags": {"mode": "readonly"},
        }
