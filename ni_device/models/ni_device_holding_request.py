from odoo import fields, models


class DeviceHoldingRequest(models.Model):
    _name = "ni.device.holding.request"
    _description = "ประวัติผู้ถือครองอุปกรณ์และคำขอเปลี่ยนผู้ถือครอง"
    _order = "write_date"

    # -------------------------
    # อ้างอิงอุปกรณ์
    # -------------------------
    device_id = fields.Many2one(
        "ni.device",
        string="อุปกรณ์",
        required=True,
        ondelete="cascade",
        index=True,
    )

    # -------------------------
    # ผู้ถือครอง (ผู้ดูแล / หน่วยงาน / caregiver)
    # -------------------------
    holder_id = fields.Many2one(
        "res.partner",
        string="ผู้ถือครอง",
        required=False,
        domain=[("is_company", "=", False)],
        help="ชื่อผู้บริบาลหรือหน่วยงานที่ถือครองอุปกรณ์ในช่วงเวลานี้",
    )

    department_id = fields.Many2one(
        "hr.department",
        string="หน่วยงาน (ถ้ามี)",
    )

    # -------------------------
    # ประเภทคำขอ (Workflow)
    # -------------------------
    request_type = fields.Selection(
        [
            ("request_hold", "ขอถือครอง"),
            ("request_return", "ขอคืนอุปกรณ์"),
            ("request_transfer", "ขอเปลี่ยนผู้ถือครอง"),
            ("request_dispose", "ขอจำหน่าย"),
        ],
        required=True,
    )

    # -------------------------
    # Workflow State
    # -------------------------
    state = fields.Selection(
        [
            ("draft", "ร่าง"),
            ("waiting", "รออนุมัติ"),
            ("approved", "อนุมัติแล้ว"),
            ("rejected", "ถูกปฏิเสธ"),
        ],
        string="สถานะ",
        default="draft",
        index=True,
    )

    # เฉพาะตอน transfer — เลือกผู้ถือใหม่
    new_holder_id = fields.Many2one("res.partner", string="ผู้ถือใหม่")
    # กรณี transfer → ให้ new holder รับทราบ (ไม่บังคับ)
    acknowledged = fields.Boolean(string="ผู้ถือใหม่รับทราบ")

    # -------------------------
    # ระบบอนุมัติ
    # -------------------------
    approved_by = fields.Many2one(
        "res.users",
        string="ผู้อนุมัติ",
        readonly=True,
    )

    approve_date = fields.Datetime(
        string="วันที่อนุมัติ",
        readonly=True,
    )

    request_reason = fields.Text(
        string="เหตุผลที่ขออนุมัติ",
    )

    # -------------------------
    # หมายเหตุ
    # -------------------------

    approval_note = fields.Text(
        string="หมายเหตุการอนุมัติ",
    )

    def action_approve(self):
        for rec in self:
            rec.state = "approved"
            rec.approve_date = fields.Datetime.now()

            device = rec.device_id

            if rec.request_type == "request_hold":
                device.holder_id = rec.holder_id
                device.state = "in_use"

            elif rec.request_type == "request_return":
                device.holder_id = False
                device.state = "available"

            elif rec.request_type == "request_transfer":
                device.holder_id = rec.new_holder_id

            elif rec.request_type == "request_dispose":
                device.holder_id = False
                device.state = "disposed"
