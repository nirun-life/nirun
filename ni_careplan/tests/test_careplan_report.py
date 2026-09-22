#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestCareplanReport(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "Careplan Report Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.state_active = cls.env.ref("ni_goal.goal_state_active")
        cls.observation_type = cls.env["ni.observation.type"].create(
            {
                "name": "Careplan Report Measure",
                "code": "test-careplan-report-measure",
                "value_type": "float",
                "min": 0,
                "max": 9999,
            }
        )
        cls.observation = cls.env["ni.observation"].create(
            {
                "patient_id": cls.patient.id,
                "type_id": cls.observation_type.id,
                "occurrence": "2026-01-01 00:00:00",
                "value_float": 50.0,
            }
        )
        cls.condition = cls.env["ni.condition"].create(
            {"patient_id": cls.patient.id, "name": "Test Diagnosis"}
        )
        cls.careplan = cls.env["ni.careplan"].create(
            {
                "patient_id": cls.patient.id,
                "condition_ids": [(6, 0, [cls.condition.id])],
                "observation_ids": [(6, 0, [cls.observation.id])],
            }
        )
        cls.env["ni.goal"].create(
            {
                "name": "Test Goal",
                "careplan_id": cls.careplan.id,
                "patient_id": cls.patient.id,
                "state_id": cls.state_active.id,
                "observation_type_id": cls.observation_type.id,
                "target_min": 0,
                "target_max": 100,
            }
        )
        cls.env["ni.service.request"].create(
            {
                "patient_id": cls.patient.id,
                "careplan_id": cls.careplan.id,
                "name": "Test Service",
                "intent": "plan",
            }
        )
        cls.env["ni.medication.request"].create(
            {
                "patient_id": cls.patient.id,
                "careplan_id": cls.careplan.id,
                "name": "Test Medication",
                "quantity": 1,
            }
        )

    def test_careplan_report_renders_without_error(self):
        html, report_type = self.env["ir.actions.report"]._render_qweb_html(
            "ni_careplan.careplan_action_report", self.careplan.ids
        )

        self.assertEqual(report_type, "html")
        for expected in (
            b"Test Diagnosis",
            b"Test Goal",
            b"Test Service",
            b"Test Medication",
        ):
            self.assertIn(expected, html)
