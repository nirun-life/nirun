from odoo import fields, models


class PatientArchiveWizard(models.TransientModel):
    _name = "ni.patient.archive.wizard"
    _description = "Patient Archive Wizard"

    patient_id = fields.Many2one(
        "ni.patient",
        string="Patient",
        required=True,
        default=lambda self: self.env.context.get("default_patient_id"),
    )
    state_reason_id = fields.Many2one(
        "ni.patient.state.reason",
        string="State Reason",  # ชัดเจนว่าคือเหตุผลที่ทำให้เข้าสู่สถานะนี้
        required=True,
    )
    state_date = fields.Date(
        string="State Date", default=fields.Date.context_today  # วันที่เข้าสู่สถานะนี้
    )
    state_note = fields.Text(string="Additional Details")  # รายละเอียดเพิ่มเติม

    def action_register_departure(self):
        patient = self.patient_id
        if self.env.context.get("toggle_active", False) and patient.active:
            patient.with_context(no_wizard=True).toggle_active()

        # เตรียมค่าที่จะเขียนลงใน patient
        vals = {
            "state_reason_id": self.state_reason_id.id,
            "state_note": self.state_note,
            "state_date": self.state_date,
            "active": False,
        }

        # ถ้าเหตุผลคือเสียชีวิต → อัพเดท deceased_date
        if self.state_reason_id.code == "deceased":
            vals["deceased_date"] = self.state_date

        patient.write(vals)
