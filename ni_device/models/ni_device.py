import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Device(models.Model):
    _name = "ni.device"
    _inherit = ["ni.identifier.mixin"]
    _rec_name = "name"
    _description = "ทะเบียนอุปกรณ์ตรวจสุขภาพ"

    name = fields.Char(string="ชื่ออุปกรณ์")

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
            ("destroyed", "ทำลายแล้ว"),
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

    holding_status = fields.Selection(
        [
            ("available", "ว่าง"),
            ("pending", "รอการอนุมัติ"),
            ("in_use", "ถูกถือครอง"),
            ("disposed", "จำหน่ายแล้ว"),
        ],
        string="สถานะการถือครอง",
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

    is_holder = fields.Boolean(compute="_compute_is_holder", store=False)

    @api.depends("holder_id")
    def _compute_is_holder(self):
        current_user = self.env.user
        for rec in self:
            rec.is_holder = rec.holder_id.user_id == current_user

    def action_request_hold(self):
        for rec in self:
            _logger.info(
                "action_request_hold called for device ID %s (%s)", rec.id, rec.name
            )
        return True

    def action_request_return(self):
        for rec in self:
            _logger.info(
                "action_request_return called for device ID %s (%s)", rec.id, rec.name
            )
        return True

    def action_request_transfer(self):
        for rec in self:
            _logger.info(
                "action_request_transfer called for device ID %s (%s)", rec.id, rec.name
            )
        return True

    def action_request_dispose(self):
        for rec in self:
            _logger.info(
                "action_request_dispose called for device ID %s (%s)", rec.id, rec.name
            )
        return True

    def action_repair(self):
        for rec in self:
            _logger.info("action_repair called for device ID %s (%s)", rec.id, rec.name)
        return True
