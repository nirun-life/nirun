#  Copyright (c) 2025 NSTDA

from odoo import fields
from odoo.exceptions import UserError

from .common import TestPatientCommon


class TestPatientArchiveWizard(TestPatientCommon):
    def test_archive_many_patients_share_one_reason(self):
        patients = self.env["ni.patient"].create(
            [
                {"partner_id": self.env["res.partner"].create({"name": name}).id}
                for name in ("Ada", "Grace")
            ]
        )
        reason = self.env.ref("ni_patient.reason_deceased")
        today = fields.Date.today()

        wizard = (
            self.env["ni.patient.archive.wizard"]
            .with_context(default_patient_ids=patients.ids)
            .create({"state_reason_id": reason.id, "state_date": today})
        )
        self.assertEqual(wizard.patient_ids, patients, "context default fills all ids")
        self.assertEqual(wizard.patient_count, 2, "หลายคน -> โชว์ tag พร้อม label")

        wizard.action_register_departure()

        for patient in patients:
            self.assertFalse(patient.active)
            self.assertEqual(patient.state_reason_id, reason)
            self.assertEqual(patient.state_date, today)
            self.assertEqual(patient.deceased_date, today)

    def test_archive_one_patient_shows_its_name(self):
        patient = self.env["ni.patient"].create(
            {"partner_id": self.env["res.partner"].create({"name": "Ada"}).id}
        )
        wizard = (
            self.env["ni.patient.archive.wizard"]
            .with_context(default_patient_ids=patient.ids)
            .create({"state_reason_id": self.env.ref("ni_patient.reason_moved").id})
        )
        self.assertEqual(wizard.patient_count, 1, "คนเดียว -> โชว์ชื่อใหญ่")
        self.assertEqual(wizard.patient_name, patient.display_name)

        wizard.action_register_departure()

        self.assertFalse(patient.active)
        self.assertEqual(wizard.state_reason_id, patient.state_reason_id)

    def test_archive_without_patient_raises(self):
        # patient_ids มาจาก context ทางเดียว — context หลุดต้อง error ไม่ใช่ปิดเงียบ
        wizard = self.env["ni.patient.archive.wizard"].create(
            {"state_reason_id": self.env.ref("ni_patient.reason_moved").id}
        )
        with self.assertRaises(UserError):
            wizard.action_register_departure()
