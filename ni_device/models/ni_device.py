from odoo import fields, models


class Device(models.Model):
    _name = "ni.device"
    _inherit = ["ni.identifier.mixin"]
    _rec_name = "name"
    _description = "ทะเบียนอุปกรณ์ตรวจสุขภาพ"

    name = fields.Char(string="ชื่ออุปกรณ์")

    # # FHIR: Device.displayName / Device.name.value
    # display_name = fields.Char("ชื่ออุปกรณ์")

    _order = "name"

    # FHIR: Device.identifier
    identifier = fields.Char("รหัสอ้างอิง", readonly=True)

    # ---------------------------
    # FHIR–Mapped Fields
    # ---------------------------

    # manufacturer → Device.manufacturer
    manufacturer = fields.Char("ชื่อผู้ผลิตอุปกรณ์")

    # manufactureDate → Device.manufactureDate
    manufacture_date = fields.Date("วันที่ผลิต")

    # serialNumber → Device.serialNumber
    serial_number = fields.Char("Serial Number")

    # modelNumber → Device.modelNumber
    model_number = fields.Char("ชื่อรุ่น (Model)")

    # ราคา (ไม่มีใน FHIR → ใช้ extension)
    price = fields.Float("ราคา")

    # Device.type (CodeableConcept)
    type_id = fields.Many2one(
        "ni.device.type",
        string="ประเภทของอุปกรณ์",
        help="เช่น เครื่องวัดความดัน, เครื่องชั่งน้ำหนัก, เครื่องวัดอุณหภูมิ",
    )

    # Device.availabilityStatus
    availability_status = fields.Selection(
        [
            ("available", "พร้อมใช้งาน"),
            ("damaged", "ชำรุด"),
            ("lost", "สูญหาย"),
        ],
        string="สถานะความพร้อมใช้งาน",
        default="available",
    )

    # รูปภาพประกอบอุปกรณ์ (FHIR ไม่มี → ใช้ image field ของ Odoo)
    image_1920 = fields.Image("รูปภาพประกอบอุปกรณ์", max_width=1920, max_height=1920)

    metric_ids = fields.Many2many(
        "ni.device.metric",
        string="ประเภทข้อมูลตรวจวัดสุขภาพที่รองรับ",
        help="จาก FHIR DeviceMetric เช่น Blood Pressure, Temperature, Weight",
    )

    status = fields.Selection(
        [
            ("available", "ว่าง"),
            ("in_use", "ถูกถือครอง"),
            ("disposed", "จำหน่ายแล้ว"),
        ],
        string="สถานะอุปกรณ์",
        store=True,
    )

    holder_ids = fields.One2many(
        "ni.device.holder",
        "device_id",
        string="ประวัติผู้ถือครอง",
    )

    holder_id = fields.Many2one(
        "res.partner", string="ผู้ถือครองอุปกรณ์ปัจจุบัน", store=True, readonly=True
    )
