from odoo import fields, models


class DeviceRepairHistory(models.Model):
    _name = "ni.device.repair"
    _description = "ประวัติการซ่อมแซมอุปกรณ์"
    _rec_name = "identifier"
    _inherit = ["ni.identifier.mixin", "image.mixin"]

    device_id = fields.Many2one(
        "ni.device",
        string="อุปกรณ์",
        required=True,
        ondelete="cascade",
    )

    # วันที่อุปกรณ์เกิดการชำรุดเสียหาย (Requirement)
    damage_date = fields.Datetime(
        string="วันที่ชำรุด", required=True, default=fields.Datetime.now
    )

    # # วันที่นำอุปกรณ์ไปซ่อม (optional แต่ควรมี)
    # repair_start_date = fields.Datetime(
    #     string="วันที่เริ่มซ่อม"
    # )
    #
    # # วันที่ซ่อมเสร็จ (ใช้คำนวณระยะเวลา)
    # repair_end_date = fields.Datetime(
    #     string="วันที่ซ่อมเสร็จ"
    # )

    # ระยะเวลาซ่อม (Requirement)
    repair_duration = fields.Float(string="ระยะเวลาซ่อม (วัน)")

    # ค่าใช้จ่ายในการซ่อมแซม (Requirement)
    repair_cost = fields.Float(string="ค่าใช้จ่ายในการซ่อม", digits=(12, 2))

    # ใครเป็นผู้ซ่อม (optional)
    technician_id = fields.Many2one(
        "res.partner", string="ช่างผู้ซ่อม", domain=[("is_company", "=", False)]
    )

    # รายละเอียดเพิ่มเติม
    note = fields.Text(string="รายละเอียดเพิ่มเติม")

    # สถานะกระบวนการซ่อม (optional แต่สำคัญ)
    state = fields.Selection(
        [
            ("damaged", "ชำรุด"),
            ("repairing", "กำลังซ่อม"),
            ("completed", "ซ่อมเสร็จ"),
        ],
        default="damaged",
        string="สถานะ",
    )

    # ==============================
    # Compute fields
    # ==============================
    # @api.depends("repair_start_date", "repair_end_date")
    # def _compute_repair_duration(self):
    #     for rec in self:
    #         if rec.repair_start_date and rec.repair_end_date:
    #             delta = rec.repair_end_date - rec.repair_start_date
    #             rec.repair_duration = delta.total_seconds() / 86400  # วัน
    #         else:
    #             rec.repair_duration = 0
