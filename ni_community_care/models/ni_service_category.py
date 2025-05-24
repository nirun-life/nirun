from odoo import api, fields, models


class ServiceCategory(models.Model):
    _inherit = "ni.service.category"

    category_count_in_approval = fields.Integer(
        compute="_compute_category_count_in_approval"
    )

    @api.depends_context("approval_id")  # ใช้ context เพื่อรับ approval ที่ต้องการ
    def _compute_category_count_in_approval(self):
        approval_id = self.env.context.get("approval_id")
        if not approval_id:
            for rec in self:
                rec.category_count_in_approval = 0
            return

        approval = self.env["ni.service.event.approval"].browse(approval_id)
        for rec in self:
            rec.category_count_in_approval = len(
                approval.event_ids.filtered(
                    lambda e: e.service_category_id.id == rec.id
                )
            )

    plan_patient_in_approval = fields.Integer(
        string="จำนวนผู้ป่วยจาก Approval นี้",
        compute="_compute_plan_patient_in_approval",
    )

    @api.depends_context("approval_id")
    def _compute_plan_patient_in_approval(self):
        approval_id = self.env.context.get("approval_id")
        Approval = self.env["ni.service.event.approval"]
        if not approval_id:
            for rec in self:
                rec.plan_patient_in_approval = 0
            return

        approval = Approval.browse(approval_id)
        for rec in self:
            # หา event ของ approval นี้ที่ใช้ category นี้
            events = approval.event_ids.filtered(
                lambda e: e.service_category_id.id == rec.id
            )
            # รวมผู้ป่วยจาก plan_patient_ids ของ event เหล่านั้น
            patients = events.mapped("plan_patient_ids")
            rec.plan_patient_in_approval = len(set(patients.ids))  # นับแบบไม่ซ้ำ
