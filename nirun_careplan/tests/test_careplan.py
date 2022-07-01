#  Copyright (c) 2021 NSTDA

from .common import TestCareplanCommon


class TestPatient(TestCareplanCommon):
    def setUp(self):
        super(TestPatient, self).setUp()
        self.careplan = self.env["ni.careplan"].with_user(self.care_manager)
        self.activity = self.env["ni.careplan.activity"].with_user(self.care_manager)
        self.activity_code = self.env["ni.careplan.activity.code"].with_user(
            self.caregiver
        )

    def test_category(self):
        # nothing to test now
        self.assertEqual(1, 1)
