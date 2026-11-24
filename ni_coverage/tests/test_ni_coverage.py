#  Copyright (c) 2026 NSTDA

from datetime import datetime

from psycopg2 import IntegrityError

from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase
from odoo.tools import mute_logger


class TestCoverage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["ni.patient"].create(
            {"partner_id": cls.env["res.partner"].create({"name": "Coverage P."}).id}
        )
        cls.issuer = cls.env["res.partner"].create(
            {"name": "Test Insurer", "is_company": True}
        )
        cls.coverage_type = cls.env["ni.coverage.type"].create(
            {"name": "Test Coverage Type", "code": "TCT"}
        )
        cls.copay = cls.env["ni.coverage.copay"].create(
            [{"name": f"Test Copay {i}", "code": f"TCP{i}"} for i in range(2)]
        )
        cls.plan = cls.env["ni.insurance.plan"].create(
            {
                "name": "Test Plan",
                "code": "TPL",
                "alias": "TP",
                "type_id": cls.coverage_type.id,
                "issuer_id": cls.issuer.id,
                "benefit_ids": [
                    (0, 0, {"type_id": copay.id, "value": 100.0}) for copay in cls.copay
                ],
            }
        )

    def _create_coverage(self, **kwargs):
        vals = {"name": "Test Coverage", "patient_id": self.patient.id}
        return self.env["ni.coverage"].create({**vals, **kwargs})

    def test_create_with_period(self):
        coverage = self._create_coverage(
            period_start=datetime(2026, 1, 1, 1, 0),
            period_end=datetime(2026, 12, 31, 16, 0),
        )
        self.assertEqual(str(coverage.period_start_date), "2026-01-01")
        self.assertEqual(str(coverage.period_end_date), "2026-12-31")
        self.assertEqual(coverage.duration_months, 11)

    def test_create_without_period(self):
        self.assertFalse(self._create_coverage().period_start)

    def test_select_plan(self):
        form = Form(self.env["ni.coverage"])
        form.patient_id = self.patient
        form.insurance_plan_id = self.plan
        coverage = form.save()
        self.assertEqual(coverage.name, "Test Plan")
        self.assertEqual(coverage.type_id, self.coverage_type)
        self.assertEqual(coverage.beneficiary_id, self.patient.partner_id)
        self.assertEqual(coverage.insurance_plan_cost_ids, self.plan.benefit_ids)
        self.assertEqual(len(self.plan.benefit_ids), 2, "The plan must not change")

    def test_select_plan_without_benefit(self):
        self.plan.benefit_ids.unlink()
        form = Form(self.env["ni.coverage"])
        form.patient_id = self.patient
        form.insurance_plan_id = self.plan
        self.assertEqual(form.save().type_id, self.coverage_type)

    def test_coverage_display_name(self):
        coverage = self._create_coverage(state="active")
        self.assertEqual(coverage.display_name, "Test Coverage")
        self.assertEqual(
            coverage.with_context(show_patient=True).display_name,
            "Coverage P., Test Coverage",
        )
        self.assertEqual(
            coverage.with_context(show_state=True).display_name,
            "Test Coverage (Active)",
        )
        self.assertEqual(
            coverage.with_context(show_patient=True, show_state=True).display_name,
            "Coverage P., Test Coverage (Active)",
        )
        coverage.state = "cancelled"
        self.assertEqual(
            coverage.with_context(show_state=True).display_name,
            "Test Coverage (Cancelled)",
        )

    def test_coverage_display_name_with_patient_context(self):
        coverage = self._create_coverage()
        self.patient.identifier = "HN-TEST"
        self.assertEqual(
            coverage.with_context(show_patient=True, show_identifier=True).display_name,
            "HN-TEST  Coverage P., Test Coverage",
        )

    def test_coverage_type_display_name(self):
        child = self.env["ni.coverage.type"].create(
            {"name": "Child", "code": "TCC", "parent_id": self.coverage_type.id}
        )
        self.assertEqual(self.coverage_type.display_name, "Test Coverage Type")
        self.assertEqual(
            self.coverage_type.with_context(show_code=True).display_name,
            "Test Coverage Type [TCT]",
        )
        self.assertEqual(child.display_name, "Test Coverage Type Child")
        self.assertEqual(
            child.with_context(show_code=True).display_name,
            "Test Coverage Type Child [TCT/TCC]",
        )
        self.coverage_type.code = "TCX"
        self.assertEqual(
            child.with_context(show_code=True).display_name,
            "Test Coverage Type Child [TCX/TCC]",
        )
        child.name = "Test Coverage Type, child"
        self.assertEqual(child.display_name, "Test Coverage Type, child")
        self.assertEqual(self.coverage_type.child_count, 1)

    def test_coverage_type_recursion(self):
        child = self.env["ni.coverage.type"].create(
            {"name": "Child", "code": "TCC", "parent_id": self.coverage_type.id}
        )
        with self.assertRaises(UserError):
            self.coverage_type.parent_id = child

    def test_plan_display_name(self):
        plan = self.plan
        self.assertEqual(plan.display_name, "Test Insurer, Test Plan")
        self.assertEqual(plan.with_context(show_issuer=False).display_name, "Test Plan")
        self.assertEqual(
            plan.with_context(show_alias=True).display_name,
            "Test Insurer, Test Plan (TP)",
        )
        self.assertEqual(
            plan.with_context(show_code=True).display_name,
            "[TPL] Test Insurer, Test Plan",
        )
        plan.issuer_id.name = "New Insurer"
        self.assertEqual(plan.display_name, "New Insurer, Test Plan")
        plan.issuer_id = False
        self.assertEqual(plan.display_name, "Test Plan")

    def test_plan_patient_count(self):
        coverage = self._create_coverage(insurance_plan_id=self.plan.id, state="active")
        self.assertEqual(self.plan.patient_count, 1)
        self.assertEqual(self.plan.patient_ids, self.patient)
        coverage.state = "cancelled"
        self.assertEqual(self.plan.patient_count, 0)

    def test_patient_main_coverage(self):
        self.assertFalse(self.patient.coverage_id)
        self._create_coverage(sequence=2)
        first = self._create_coverage(name="First", sequence=1)
        self.assertEqual(self.patient.coverage_id, first)

    def test_benefit_type_unique(self):
        benefit = {"type_id": self.copay[0].id, "value": 10.0}
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            self._create_coverage(benefit_ids=[(0, 0, benefit), (0, 0, benefit)])

    def test_plan_benefit_type_unique(self):
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            self.plan.benefit_ids = [(0, 0, {"type_id": self.copay[0].id})]
