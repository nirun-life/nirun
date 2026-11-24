#  Copyright (c) 2026 NSTDA

from datetime import datetime

from odoo.tests import TransactionCase


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

    def test_sent_time_is_kept(self):
        communication = self._create_communication()
        communication.flush_recordset()
        communication.invalidate_recordset()
        sent = datetime(2026, 1, 1, 1)
        self.assertEqual(communication.period_start, sent)
        self.assertEqual(communication.occurrence, sent)
        self.assertEqual(communication.event_id.occurrence, sent)
