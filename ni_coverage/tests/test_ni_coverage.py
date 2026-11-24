#  Copyright (c) 2026 NSTDA

from datetime import datetime

from odoo.tests import Form, TransactionCase


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
