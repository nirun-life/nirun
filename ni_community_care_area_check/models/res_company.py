# Copyright 2025
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    attendance_geocode_service = fields.Selection(
        selection=[
            ("none", "ไม่ตรวจสอบพื้นที่"),
            ("nominatim", "Nominatim (OpenStreetMap)"),
            ("longdo", "Longdo Map API"),
        ],
        string="บริการ Geocoding",
        default="nominatim",
        required=True,
        help="เลือกบริการ reverse geocoding สำหรับตรวจสอบพื้นที่เช็คอิน/เช็คเอาท์",
    )
    attendance_longdo_api_key = fields.Char(
        string="Longdo API Key",
        help="API Key สำหรับ Longdo Map (จำเป็นเมื่อเลือก Longdo Map API)",
    )
