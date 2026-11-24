#  Copyright (c) 2026 NSTDA

from datetime import datetime

from odoo.tests import Form, TransactionCase


class TestCommunication(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["ni.patient"].create(
            {
                "partner_id": cls.env["res.partner"]
                .create({"name": "Communication P."})
                .id
            }
        )
        cls.category = cls.env["ni.communication.category"].create(
            {"name": "Test Category", "code": "TCA"}
        )

    def _create_communication(self, **kwargs):
        return self.env["ni.communication"].create(
            {
                "patient_id": self.patient.id,
                "category_id": self.category.id,
                "period_start": "2026-01-01 01:00:00",
                **kwargs,
            }
        )

    def test_create_without_sender_employee(self):
        communication = self._create_communication(sender_employee_id=False)
        self.assertFalse(communication.sender_employee_id)
        self.assertEqual(communication.sender_id, self.env.user.partner_id)

    def test_search_by_name(self):
        communication = self._create_communication()
        model = self.env["ni.communication"]
        self.assertIn(communication.id, dict(model.name_search("Test Category")))
        self.assertIn(
            communication.id, dict(model.name_search(communication.identifier))
        )
        self.assertNotIn(communication.id, dict(model.name_search("Nothing")))

    def test_summary_with_content(self):
        content = self.env["ni.communication.content"].create(
            {"name": "Drink water", "code": "TDW", "category_id": self.category.id}
        )
        communication = self._create_communication(content_ids=[(6, 0, content.ids)])
        self.assertEqual(communication.event_id.summary, "Test Category; Drink water")

    def test_discharge_communication_domain(self):
        field = self.env["ni.encounter"].fields_get(["discharge_communication_id"])
        self.assertEqual(
            field["discharge_communication_id"]["domain"],
            "[('encounter_id', '=', id)]",
        )

    def test_name(self):
        communication = self._create_communication()

        def name(**context):
            return communication.with_context(**context).display_name

        self.assertEqual(name(), "Test Category")
        self.assertEqual(name(show_patient=True), "Communication P.: Test Category")
        self.assertEqual(name(show_state=True), "Test Category (Completed)")
        self.assertEqual(
            name(show_identifier=True), f"Test Category - {communication.identifier}"
        )

    def test_sender_of_employee(self):
        work_contact = self.env["res.partner"].create({"name": "Work contact"})
        employee = self.env["hr.employee"].create(
            {"name": "Sender", "work_contact_id": work_contact.id}
        )
        communication = self._create_communication(sender_employee_id=employee.id)
        self.assertEqual(communication.sender_id, work_contact)
        employee.user_id = self.env["res.users"].create(
            {"name": "Sender user", "login": "sender.user"}
        )
        communication = self._create_communication(sender_employee_id=employee.id)
        self.assertEqual(communication.sender_id, employee.user_id.partner_id)

    def test_count(self):
        encounter = self.env["ni.encounter"].create(
            {
                "patient_id": self.patient.id,
                "class_id": self.env.ref("ni_patient.class_AMB").id,
                "period_start": "2025-12-01 01:00:00",
            }
        )
        self._create_communication(encounter_id=encounter.id)
        self._create_communication()
        self.assertEqual(encounter.communication_count, 1)
        self.assertEqual(self.patient.communication_count, 2)
        action = encounter.action_communication()
        self.assertEqual(action["context"]["default_encounter_id"], encounter.id)
        self.assertTrue(self.patient.action_communication())

    def test_default_recipient(self):
        form = Form(
            self.env["ni.communication"].with_context(
                default_patient_id=self.patient.id
            )
        )
        self.assertEqual(form.recipient_ids[:], self.patient.partner_id)

    def test_discharge(self):
        encounter = self.env["ni.encounter"].create(
            {
                "patient_id": self.patient.id,
                "class_id": self.env.ref("ni_patient.class_AMB").id,
                "state": "in-progress",
                "period_start": "2025-12-01 01:00:00",
            }
        )
        content = self.env["ni.communication.content"].create(
            {
                "name": "Rest",
                "code": "TRS",
                "category_id": self.env.ref("ni_communication.categ_suggestion").id,
            }
        )
        wizard = (
            self.env["ni.encounter.discharge.wizard"]
            .with_context(default_encounter_id=encounter.id)
            .create(
                {
                    "suggest_content_ids": [(6, 0, content.ids)],
                    "discharge_status_id": self.env["ni.encounter.discharge.status"]
                    .search([], limit=1)
                    .id,
                    "discharge_disposition_id": self.env[
                        "ni.encounter.discharge.disposition"
                    ]
                    .search([], limit=1)
                    .id,
                }
            )
        )
        wizard.discharge()
        self.assertEqual(encounter.discharge_communication_content_ids, content)

    def test_sent_time_is_kept(self):
        communication = self._create_communication()
        communication.flush_recordset()
        communication.invalidate_recordset()
        sent = datetime(2026, 1, 1, 1)
        self.assertEqual(communication.period_start, sent)
        self.assertEqual(communication.occurrence, sent)
        self.assertEqual(communication.event_id.occurrence, sent)
