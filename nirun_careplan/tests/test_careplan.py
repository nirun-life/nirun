#  Copyright (c) 2021 Piruin P.

from .common import TestCareplanCommon


class TestPatient(TestCareplanCommon):
    def setUp(self):
        super(TestPatient, self).setUp()
        self.careplan = self.env["ni.careplan"].with_user(self.care_manager)
        self.activity = self.env["ni.careplan.activity"].with_user(self.care_manager)

    def test_category(self):
        self.miss_glenda = self.ref("nirun_patient.mrs_glenda")

        category = [
            self.ref("nirun_careplan.category_health"),
            self.ref("nirun_careplan.category_social"),
        ]
        plan = self.careplan.create(
            {"category_ids": [[6, 0, category]], "patient_id": self.miss_glenda}
        )

        self.assertEqual(2, len(plan.category_ids))

        memory = self.ref("nirun_careplan.category_memory")
        self.activity.create(
            {"name": "Activity 1", "careplan_id": plan.id, "category_id": memory}
        )
        self.assertTrue(memory in plan.mapped("category_ids.id"))

        act = self.activity.create(
            {
                "name": "Activity 2",
                "careplan_id": plan.id,
                "category_id": self.ref("nirun_careplan.category_health"),
            }
        )

        act.category_id = self.ref("nirun_careplan.category_mental")
        self.assertEqual(4, len(plan.category_ids))

        act.category_id = None
        self.assertEqual(4, len(plan.category_ids))
