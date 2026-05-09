from odoo import _, api, fields, models


class DeviceRequest(models.Model):
    _name = "ni.device.request"
    _description = "Device Holding Change Request"
    _inherit = ["ni.identifier.mixin", "image.mixin", "ni.holder.mixin"]
    _rec_name = "identifier"

    _order = "create_date DESC"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    device_id = fields.Many2one(
        "ni.device",
        string="Device",
        required=True,
        index=True,
        check_company=True,
        ondelete="cascade",
    )
    device_image = fields.Image(related="device_id.image_1920", string="Device Image")
    device_identifier = fields.Char(
        related="device_id.identifier", string="Device Identifier"
    )

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

    new_holder_partner_id = fields.Many2one(
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

    is_transfer_to_me = fields.Boolean(
        compute="_compute_is_transfer_to_me",
        search="_search_is_transfer_to_me",
    )

    # -------------------------
    # Approval System
    # -------------------------
    approved_by = fields.Many2one(
        "res.users",
        string="By",
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
                rec.new_holder_partner_id = False

    @api.onchange("new_holder_employee_id")
    def _onchange_new_holder_employee(self):
        for rec in self:
            if rec.new_holder_employee_id:
                # autofill partner จาก employee
                partner = (
                    rec.new_holder_employee_id.user_id.partner_id
                    or rec.new_holder_employee_id.address_home_id
                )
                rec.new_holder_partner_id = partner  # สำหรับ field new_holder_id

                if rec.request_type == "request_hold":
                    rec.holder_employee_id = rec.new_holder_employee_id.id
                    rec.holder_partner_id = partner

    # ---------------------------------------------------
    # Compute Fields
    # ---------------------------------------------------

    @api.depends("new_holder_employee_id", "new_holder_partner_id")
    def _compute_new_holder_name(self):
        for rec in self:
            rec.new_holder_name = (
                rec.new_holder_employee_id.name or rec.new_holder_partner_id.name or ""
            )

    @api.depends("new_holder_partner_id", "new_holder_partner_id.user_id")
    def _compute_is_transfer_to_me(self):
        user = self.env.user
        partner = user.partner_id

        for rec in self:
            rec.is_transfer_to_me = (
                rec.request_type == "request_transfer"
                and rec.new_holder_partner_id
                and (
                    rec.new_holder_partner_id.user_id == user
                    or rec.new_holder_partner_id == partner
                )
            )

    def _search_is_transfer_to_me(self, operator, value):
        if operator not in ("=", "!="):
            raise NotImplementedError()

        user = self.env.user
        partner = user.partner_id

        domain = [
            ("request_type", "=", "request_transfer"),
            ("new_holder_partner_id", "!=", False),
            "|",
            ("new_holder_partner_id.user_id", "=", user.id),
            ("new_holder_partner_id", "=", partner.id),
        ]

        if (operator == "=" and not value) or (operator == "!=" and value):
            return ["!"] + domain

        return domain

    @api.depends("device_id", "device_id.image_1920")
    def _compute_device_image(self):
        for rec in self.with_context(bin_size=False):
            rec.device_image_1920 = rec.device_id.image_1920

    def action_submit(self):
        for rec in self.sudo():
            device = rec.device_id

            # state ของ request
            rec.state = "pending"

            if rec.request_type == "request_hold":
                # device ต้องว่างก่อน
                rec.holder_employee_id = rec.new_holder_employee_id.id
                rec.holder_partner_id = rec.new_holder_partner_id.id
                if device.state == "available":
                    device.write(
                        {
                            "state": "pending",
                        }
                    )

    def action_approve(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Approve Request"),
            "res_model": "ni.device.request",
            "res_id": self.id,  # <<< record เดิม
            "view_mode": "form",
            "view_id": self.env.ref(
                "ni_device.ni_device_request_view_form_wizard_approval"
            ).id,
            "target": "new",
            "context": {
                "approval_action": "approve",
            },
        }

    def action_reject(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Reject Request"),
            "res_model": "ni.device.request",
            "res_id": self.id,  # <<< record เดิม
            "view_mode": "form",
            "view_id": self.env.ref(
                "ni_device.ni_device_request_view_form_wizard_approval"
            ).id,
            "target": "new",
            "context": {
                "approval_action": "reject",
            },
        }

    def action_confirm_approval(self):
        for rec in self:
            action = rec.env.context.get("approval_action")

            if action == "approve":
                rec._action_approve_confirm()
            elif action == "reject":
                rec._action_reject_confirm()

    def _action_approve_confirm(self):
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
                        "holder_partner_id": rec.holder_partner_id.id
                        if rec.holder_partner_id
                        else False,
                        "start_date": approve_date,
                        "request_id": rec.id,
                    }
                )

                # อัปเดต device
                device.holder_employee_id = rec.holder_employee_id
                device.holder_partner_id = rec.holder_partner_id
                device.state = "in_use"

            # ==================================================
            # 2) RETURN หรือ DISPOSE → ปิดประวัติเดิม (end_date)
            # ==================================================
            elif rec.request_type in ["request_return", "request_dispose"]:
                if last_history:
                    last_history.end_date = approve_date

                if rec.request_type in ["request_dispose"]:
                    device.disposed_date = approve_date
                    device.availability_status = "disposed"

                # อัปเดต device
                device.holder_employee_id = False
                device.holder_partner_id = False
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
                        "holder_partner_id": rec.new_holder_partner_id.id
                        if rec.new_holder_partner_id
                        else False,
                        "start_date": approve_date,
                        "request_id": rec.id,
                    }
                )

                # อัปเดต device
                device.holder_employee_id = rec.new_holder_employee_id
                device.holder_partner_id = rec.new_holder_partner_id
                device.state = "in_use"

    def _action_reject_confirm(self):
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
                if rec.is_transfer_to_me:
                    rec.acknowledged = True
                    rec.acknowledged_date = fields.Datetime.now()

    @api.model_create_multi
    def create(self, vals_list):
        return super(DeviceRequest, self.sudo()).create(vals_list)
