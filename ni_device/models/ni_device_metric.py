from odoo import fields, models


class DeviceMetric(models.Model):
    _name = "ni.device.metric"
    _description = "ประเภทข้อมูลตรวจวัดสุขภาพ (Device Metric)"
    _inherit = ["ni.coding"]

    # เพิ่มฟิลด์เฉพาะของ DeviceMetric (ไม่ซ้ำกับ ni.coding)

    # หน่วยของการวัด เช่น mmHg, bpm, %, °C
    unit = fields.Char(
        string="หน่วย",
        help="หน่วยของค่าที่วัด เช่น mmHg, °C, %, kg, bpm",
    )

    # Category ตาม FHIR DeviceMetric.category
    category = fields.Selection(
        [
            ("measurement", "Measurement"),
            ("setting", "Setting"),
            ("calculated", "Calculated"),
            ("unspecified", "Unspecified"),
        ],
        string="หมวดหมู่",
        default="measurement",
    )

    # ความถี่ในการวัด เช่น 1s, 5s, 60s (FHIR: measurementPeriod)
    measurement_period = fields.Char(
        string="Measurement Period",
        help="ความถี่หรือรอบเวลาในการวัด เช่น 1s, 60s",
    )

    # ความสัมพันธ์ไป Device (Many2many)
    device_ids = fields.Many2many(
        "ni.device",
        string="ใช้งานในอุปกรณ์",
    )
