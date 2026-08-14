from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PatientArchiveWizard(models.TransientModel):
    _name = "ni.patient.archive.wizard"
    _description = "Patient Archive Wizard"

    patient_ids = fields.Many2many(
        "ni.patient",
        string="Patient",
        required=True,
    )
    # คนเดียวโชว์ชื่อใหญ่, หลายคนโชว์เป็น tag พร้อม label
    patient_count = fields.Integer(compute="_compute_patient")
    patient_name = fields.Char(compute="_compute_patient")
    state_reason_id = fields.Many2one(
        "ni.patient.state.reason",
        string="State Reason",  # ชัดเจนว่าคือเหตุผลที่ทำให้เข้าสู่สถานะนี้
        required=True,
    )
    state_date = fields.Date(
        string="State Date", default=fields.Date.context_today  # วันที่เข้าสู่สถานะนี้
    )
    state_note = fields.Text(string="Additional Details")  # รายละเอียดเพิ่มเติม

    @api.depends("patient_ids")
    def _compute_patient(self):
        for rec in self:
            rec.patient_count = len(rec.patient_ids)
            rec.patient_name = rec.patient_ids[:1].display_name

    def action_register_departure(self):
        # patient_ids เป็น readonly ฝั่ง client จึงมาจาก default_patient_ids ทางเดียว
        # required=True บน m2m ไม่ถูกบังคับที่ DB — ถ้า context หลุด ต้องดังกว่าเงียบ
        if not self.patient_ids:
            raise UserError(_("No patient selected."))

        # เหตุผล/วันที่/รายละเอียด ชุดเดียว ใช้กับทุกคนที่เลือกมา
        vals = {
            "state_reason_id": self.state_reason_id.id,
            "state_note": self.state_note,
            "state_date": self.state_date,
            "active": False,
        }

        # ถ้าเหตุผลคือเสียชีวิต → อัพเดท deceased_date
        if self.state_reason_id.code == "deceased":
            vals["deceased_date"] = self.state_date

        self.patient_ids.write(vals)
