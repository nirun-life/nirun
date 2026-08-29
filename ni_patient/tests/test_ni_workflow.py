#  Copyright (c) 2024 NSTDA

from odoo import fields
from odoo.tests import common


class TestWorkflow(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Workflow Test Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": cls.partner.id})
        enc_class = cls.env["ni.encounter.class"].search([], limit=1)
        cls.encounter = cls.env["ni.encounter"].create(
            {"patient_id": cls.patient.id, "class_id": enc_class.id}
        )

    def _make_event(self, **kw):
        vals = {
            "patient_id": self.patient.id,
            "encounter_id": self.encounter.id,
            "name": "Test Event",
            "type": "event",
            "state": "preparation",
            "occurrence": fields.Datetime.now(),
        }
        vals.update(kw)
        return self.env["ni.workflow.event"].create(vals)

    def _make_request(self, **kw):
        vals = {
            "patient_id": self.patient.id,
            "encounter_id": self.encounter.id,
            "name": "Test Request",
            "type": "request",
            "state": "draft",
        }
        vals.update(kw)
        return self.env["ni.workflow.request"].create(vals)

    def test_event_create(self):
        event = self._make_event()
        self.assertEqual(event.patient_id, self.patient)
        self.assertEqual(event.state, "preparation")
        self.assertEqual(event.company_id, self.patient.company_id)

    def test_request_create(self):
        request = self._make_request()
        self.assertEqual(request.state, "draft")
        self.assertFalse(request.is_replaced)

    def test_request_replacement_tracking(self):
        original = self._make_request(name="Original")
        replacement = self._make_request(name="Replacement", replace_id=original.id)
        self.assertTrue(original.is_replaced)
        self.assertIn(replacement, original.replaced_by_ids)

    def test_action_resource(self):
        event = self._make_event(res_model="ni.patient", res_id=self.patient.id)
        action = event.action_resource()
        self.assertEqual(action["res_model"], "ni.patient")
        self.assertEqual(action["res_id"], self.patient.id)
        self.assertEqual(action["views"], [[False, "form"]])

    def test_garbage_collect_removes_orphans(self):
        event = self._make_event()
        event_id = event.id
        self.env.cr.execute(
            """UPDATE ni_workflow_event
               SET res_model = NULL, res_id = NULL,
                   write_date = '2000-01-01', create_date = '2000-01-01'
               WHERE id = %s""",
            (event_id,),
        )
        self.env["ni.workflow.event"].garbage_collect()
        self.assertFalse(self.env["ni.workflow.event"].browse(event_id).exists())

    def test_garbage_collect_keeps_linked_records(self):
        event = self._make_event(res_model="ni.patient", res_id=self.patient.id)
        event_id = event.id
        self.env.cr.execute(
            "UPDATE ni_workflow_event SET write_date = '2000-01-01', create_date = '2000-01-01' WHERE id = %s",
            (event_id,),
        )
        self.env["ni.workflow.event"].garbage_collect()
        self.assertTrue(self.env["ni.workflow.event"].browse(event_id).exists())

    def test_encounter_logs_workflow_event_on_transitions(self):
        enc_class = self.env["ni.encounter.class"].search([], limit=1)
        encounter = self.env["ni.encounter"].create(
            {
                "patient_id": self.patient.id,
                "class_id": enc_class.id,
                "period_start": fields.Datetime.now(),
                "priority": "urgent",
            }
        )
        events_domain = [
            ("res_model", "=", "ni.encounter"),
            ("res_id", "=", encounter.id),
        ]

        encounter.action_confirm()
        self.assertEqual(encounter.state, "in-progress")
        events = self.env["ni.workflow.event"].search(events_domain, order="id")
        self.assertEqual(len(events), 1)
        self.assertEqual(events.state, "in-progress")
        self.assertEqual(events.summary, "{} (Urgent)".format(enc_class.name))

        encounter.action_close()
        self.assertEqual(encounter.state, "finished")
        events = self.env["ni.workflow.event"].search(events_domain, order="id")
        self.assertEqual(len(events), 2)
        self.assertEqual(events[-1].state, "completed")

        lines = self.env["ni.workflow.line"].search(events_domain)
        self.assertEqual(len(lines), 2)
