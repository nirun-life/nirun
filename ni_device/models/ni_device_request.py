from odoo import api, fields, models


class DeviceRequest(models.Model):
    _name = "ni.device.request"
    _inherit = ["ni.identifier.mixin", "image.mixin"]
    _rec_name = "identifier"

    _description = "คำขออนุมัติการถือครองอุปกรณ์"
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

    is_holder = fields.Boolean(related="device_id.is_holder")
    is_transfer_holder = fields.Boolean(compute="_compute_is_transfer_holder")

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

    @api.depends("new_holder_id", "new_holder_id.user_id")
    def _compute_is_transfer_holder(self):
        current_user = self.env.user
        current_partner = current_user.partner_id
        for rec in self:
            rec.is_transfer_holder = False
            if not rec.new_holder_id:
                continue
            # ครอบคลุมทั้งกรณี partner ถูกผูกกับ user และกรณี partner ตรงกับ user's partner
            if rec.new_holder_id.user_id and rec.new_holder_id.user_id == current_user:
                rec.is_transfer_holder = True
            elif rec.new_holder_id == current_partner:
                rec.is_transfer_holder = True
            else:
                rec.is_transfer_holder = False

    def action_submit(self):
        for rec in self:
            rec.state = "waiting"
            if rec.device_id.state == "available":
                rec.device_id.state = "pending"

                # ขอถือครอง : ถ้าอุปกรณ์ว่าง → เปลี่ยนเป็น pending
                if rec.request_type == "request_hold":
                    if rec.device_id.state == "available":
                        rec.device_id.state = "pending"

    def action_approve(self):
        for rec in self:
            rec.state = "approved"
            rec.approve_date = fields.Datetime.now()

            device = rec.device_id
            approve_date = rec.approve_date

            # หา holder ปัจจุบันในประวัติ (ที่ยังไม่ถูกปิด)
            last_history = self.env["ni.device.holder"].search(
                [("device_id", "=", device.id), ("end_date", "=", False)],
                limit=1,
                order="start_date desc",
            )

            # =============================================
            # 1) HOLD → สร้างประวัติใหม่ (start_date)
            # =============================================
            if rec.request_type == "request_hold":
                # ปิดประวัติเก่า (ถ้ามี)
                if last_history:
                    last_history.end_date = approve_date

                # สร้างประวัติใหม่
                self.env["ni.device.holder"].create(
                    {
                        "device_id": device.id,
                        "holder_id": rec.holder_id.id,
                        "start_date": approve_date,
                        "request_id": rec.id,
                    }
                )

                # อัปเดต device
                device.holder_id = rec.holder_id
                device.state = "in_use"

            # ==================================================
            # 2) RETURN หรือ DISPOSE → ปิดประวัติเดิม (end_date)
            # ==================================================
            elif rec.request_type in ["request_return", "request_dispose"]:
                if last_history:
                    last_history.end_date = approve_date

                # อัปเดต device
                device.holder_id = False
                device.state = (
                    "available" if rec.request_type == "request_return" else "disposed"
                )

            # ==================================================
            # 3) TRANSFER → ปิดเดิม + สร้างใหม่
            # ==================================================
            elif rec.request_type == "request_transfer":

                # ปิดประวัติเก่าของ holder เดิม
                if last_history:
                    last_history.end_date = approve_date

                # สร้างประวัติใหม่ของ holder ใหม่
                self.env["ni.device.holder"].create(
                    {
                        "device_id": device.id,
                        "holder_id": rec.new_holder_id.id,
                        "start_date": approve_date,
                        "request_id": rec.id,
                    }
                )

                # อัปเดต device
                device.holder_id = rec.new_holder_id
                device.state = "in_use"
