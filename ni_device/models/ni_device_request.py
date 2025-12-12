from odoo import api, fields, models


class DeviceRequest(models.Model):
    _name = "ni.device.request"
    _description = "Device Holding Change Request"
    _inherit = ["ni.identifier.mixin", "image.mixin", "ni.holder.mixin"]
    _rec_name = "identifier"

    _order = "create_date DESC"

    # -------------------------
    # อ้างอิงอุปกรณ์
    # -------------------------
    device_id = fields.Many2one(
        "ni.device",
        string="Device",
        required=True,
        ondelete="cascade",
        index=True,
    )
    device_image = fields.Image(related="device_id.image_1920", string="Device Image")
    device_identifier = fields.Char(
        related="device_id.identifier", string="Device Identifier"
    )
    company_id = fields.Many2one(related="device_id.company_id")
    is_holder = fields.Boolean(related="device_id.is_holder")

    # -------------------------
    # Request Type (Workflow)
    # -------------------------
    request_type = fields.Selection(
        [
            ("request_hold", "Request Holding"),
            ("request_return", "Return Device"),
            ("request_transfer", "Transfer Holder"),
            ("request_dispose", "Dispose Device"),
        ],
        required=True,
        string="Request Type",
    )

    request_reason = fields.Html(
        string="Request Reason",
    )

    dispose_type_id = fields.Many2one(
        "ni.device.dispose.type",
        string="Disposal Method",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        default="draft",
        index=True,
    )

    # -------------------------
    # New Holder: for request_type = request_hold || request_transfer
    # -------------------------
    new_holder_type = fields.Selection(
        [
            ("employee", "Employee"),
            ("partner", "Contact"),
        ],
        default="employee",
        string="Holder Type",
    )

    new_holder_name = fields.Char("New Holder Name", compute="_compute_new_holder_name")

    new_holder_id = fields.Many2one(
        "res.partner",
        string="New Holder",
    )
    new_holder_employee_id = fields.Many2one(
        "hr.employee",
        string="New Holder (Employee)",
        check_company=True,
    )

    acknowledged = fields.Boolean(string="Acknowledged")
    acknowledged_date = fields.Datetime(
        string="Acknowledged Date",
        readonly=True,
    )

    is_transfer_holder = fields.Boolean(compute="_compute_is_transfer_holder")

    # -------------------------
    # Approval System
    # -------------------------
    approved_by = fields.Many2one(
        "res.users",
        string="Approved By",
        readonly=True,
    )

    approve_date = fields.Datetime(
        string="Approval Date",
        readonly=True,
    )

    approval_note = fields.Html(
        string="Approval Note",
    )

    @api.onchange("new_holder_type")
    def _onchange_holder_type(self):
        for rec in self:
            if rec.new_holder_type == "partner":
                rec.new_holder_employee_id = False
                rec.new_holder_id = False

    @api.onchange("new_holder_employee_id")
    def _onchange_new_holder_employee(self):
        for rec in self:
            if rec.new_holder_employee_id:
                # autofill partner จาก employee
                partner = (
                    rec.new_holder_employee_id.user_id.partner_id
                    or rec.new_holder_employee_id.address_home_id
                )
                rec.new_holder_id = partner  # สำหรับ field new_holder_id

                if rec.request_type == "request_hold":
                    rec.holder_employee_id = rec.new_holder_employee_id.id
                    rec.holder_id = partner

    # ---------------------------------------------------
    # Compute Fields
    # ---------------------------------------------------

    @api.depends("new_holder_employee_id", "new_holder_id")
    def _compute_new_holder_name(self):
        for rec in self:
            rec.new_holder_name = (
                rec.new_holder_employee_id.name or rec.new_holder_id.name or ""
            )

    @api.depends("new_holder_id", "new_holder_id.user_id")
    def _compute_is_transfer_holder(self):

        current_user = self.env.user
        current_partner = current_user.partner_id
        for rec in self:
            rec.is_transfer_holder = False

            if rec.request_type == "request_transfer":
                if not rec.new_holder_id:
                    continue
                # ครอบคลุมทั้งกรณี partner ถูกผูกกับ user และกรณี partner ตรงกับ user's partner
                if (
                    rec.new_holder_id.user_id
                    and rec.new_holder_id.user_id == current_user
                ):
                    rec.is_transfer_holder = True
                elif rec.new_holder_id == current_partner:
                    rec.is_transfer_holder = True
                else:
                    rec.is_transfer_holder = False

    @api.depends("device_id", "device_id.image_1920")
    def _compute_device_image(self):
        for rec in self.with_context(bin_size=False):
            rec.device_image_1920 = rec.device_id.image_1920

    def action_submit(self):
        for rec in self.sudo():  # ← สำคัญ!
            rec.state = "pending"
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
            rec.approved_by = self.env.user.id
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
                        "holder_employee_id": rec.holder_employee_id.id
                        if rec.holder_employee_id
                        else False,
                        "holder_id": rec.holder_id.id if rec.holder_id else False,
                        "start_date": approve_date,
                        "request_id": rec.id,
                    }
                )

                # อัปเดต device
                device.holder_employee_id = rec.holder_employee_id
                device.holder_id = rec.holder_id
                device.state = "in_use"

            # ==================================================
            # 2) RETURN หรือ DISPOSE → ปิดประวัติเดิม (end_date)
            # ==================================================
            elif rec.request_type in ["request_return", "request_dispose"]:
                if last_history:
                    last_history.end_date = approve_date

                # อัปเดต device
                device.holder_employee_id = False
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
                        "holder_employee_id": rec.new_holder_employee_id.id
                        if rec.new_holder_employee_id
                        else False,
                        "holder_id": rec.new_holder_id.id
                        if rec.new_holder_id
                        else False,
                        "start_date": approve_date,
                        "request_id": rec.id,
                    }
                )

                # อัปเดต device
                device.holder_employee_id = rec.new_holder_employee_id
                device.holder_id = rec.new_holder_id
                device.state = "in_use"

    def action_reject(self):
        for rec in self:
            rec.state = "rejected"
            rec.approve_date = fields.Datetime.now()
            rec.approved_by = self.env.user.id
            device = rec.device_id

            if rec.request_type == "request_hold":
                device.state = "available"

    def action_acknowledged(self):
        for rec in self.sudo():
            if rec.request_type == "request_transfer":
                if rec.is_transfer_holder:
                    rec.acknowledged = True
                    rec.acknowledged_date = fields.Datetime.now()

    @api.model_create_multi
    def create(self, vals_list):
        return super(DeviceRequest, self.sudo()).create(vals_list)
