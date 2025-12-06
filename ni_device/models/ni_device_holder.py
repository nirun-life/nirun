from odoo import fields, models


class DeviceHolder(models.Model):
    _name = "ni.device.holder"
    _description = "ประวัติผู้ถือครองอุปกรณ์"
    _order = "create_date DESC"

    device_id = fields.Many2one("ni.device", string="อุปกรณ์", required=True)
    device_identifier = fields.Char(
        related="device_id.identifier", string="รหัสอ้างอิงอุปกรณ์"
    )

    holder_id = fields.Many2one("res.partner", string="ผู้ถือครอง", required=True)

    start_date = fields.Datetime(string="วันที่เริ่มถือครอง", required=True)
    end_date = fields.Datetime(string="วันที่สิ้นสุดถือครอง")

    request_id = fields.Many2one("ni.device.request", string="คำขอที่เกี่ยวข้อง")
