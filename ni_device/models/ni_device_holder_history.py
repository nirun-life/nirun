from odoo import fields, models


class DeviceHolderHistory(models.Model):
    _name = "ni.device.holder.history"
    _description = "ประวัติผู้ถือครองอุปกรณ์"

    device_id = fields.Many2one("ni.device", string="อุปกรณ์", required=True)
    holder_id = fields.Many2one("res.partner", string="ผู้ถือครอง", required=True)

    start_date = fields.Datetime(string="วันที่เริ่มถือครอง", required=True)
    end_date = fields.Datetime(string="วันที่สิ้นสุดถือครอง")

    request_id = fields.Many2one(
        "ni.device.holding.request", string="คำขอที่เกี่ยวข้อง"
    )
