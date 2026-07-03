#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestGoalTargetStatus(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "Target Status Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.state_active = cls.env.ref("ni_goal.goal_state_active")

        cls.type_numeric = cls.env["ni.observation.type"].create(
            {
                "name": "Test Numeric Measure",
                "code": "test-goal-numeric",
                "value_type": "float",
                "min": 0,
                "max": 9999,
            }
        )
        cls.type_coded = cls.env["ni.observation.type"].create(
            {
                "name": "Test Coded Measure",
                "code": "test-goal-coded",
                "value_type": "code_id",
            }
        )
        cls.code_ok = cls.env["ni.observation.value.code"].create(
            {"name": "OK", "type_ids": [(6, 0, [cls.type_coded.id])]}
        )
        cls.code_bad = cls.env["ni.observation.value.code"].create(
            {"name": "BAD", "type_ids": [(6, 0, [cls.type_coded.id])]}
        )
        cls.code_child = cls.env["ni.observation.value.code"].create(
            {
                "name": "OK Child",
                "type_ids": [(6, 0, [cls.type_coded.id])],
                "parent_id": cls.code_ok.id,
            }
        )
        cls.type_coded_multi = cls.env["ni.observation.type"].create(
            {
                "name": "Test Multi Coded Measure",
                "code": "test-goal-coded-multi",
                "value_type": "code_ids",
            }
        )
        (cls.code_ok + cls.code_bad + cls.code_child).write(
            {"type_ids": [(4, cls.type_coded_multi.id)]}
        )
        cls.code_x = cls.env["ni.observation.value.code"].create(
            {"name": "X", "type_ids": [(6, 0, [cls.type_coded_multi.id])]}
        )
        cls.code_y = cls.env["ni.observation.value.code"].create(
            {"name": "Y", "type_ids": [(6, 0, [cls.type_coded_multi.id])]}
        )

    def _make_obs(self, ob_type, occurrence, **values):
        return self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "type_id": ob_type.id,
                "occurrence": occurrence,
                **values,
            }
        )

    def _make_goal(self, ob_type, **values):
        return self.env["ni.goal"].create(
            {
                "name": "Test Goal",
                "patient_id": self.patient.id,
                "state_id": self.state_active.id,
                "observation_type_id": ob_type.id,
                **values,
            }
        )

    # ── numeric target ────────────────────────────────────────────────────

    def test_numeric_value_in_range(self):
        goal = self._make_goal(self.type_numeric, target_min=0, target_max=100)
        self._make_obs(self.type_numeric, "2026-01-01 00:00:00", value_float=50.0)
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "in_range")

    def test_numeric_value_out_of_range(self):
        goal = self._make_goal(self.type_numeric, target_min=0, target_max=100)
        self._make_obs(self.type_numeric, "2026-01-01 00:00:00", value_float=500.0)
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "out_of_range")

    def test_no_status_without_measurement(self):
        goal = self._make_goal(self.type_numeric, target_min=0, target_max=100)

        self.assertFalse(goal.target_status)

    # ── coded target ──────────────────────────────────────────────────────

    def test_coded_value_matches_target(self):
        goal = self._make_goal(
            self.type_coded,
            target_code_operator="=",
            target_code_ids=[(6, 0, [self.code_ok.id])],
        )
        self._make_obs(
            self.type_coded, "2026-01-01 00:00:00", value_code_id=self.code_ok.id
        )
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "in_range")

    def test_coded_value_does_not_match_target(self):
        goal = self._make_goal(
            self.type_coded,
            target_code_operator="=",
            target_code_ids=[(6, 0, [self.code_ok.id])],
        )
        self._make_obs(
            self.type_coded, "2026-01-01 00:00:00", value_code_id=self.code_bad.id
        )
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "out_of_range")

    def test_coded_value_matches_child_of_target(self):
        goal = self._make_goal(
            self.type_coded,
            target_code_operator="child_of",
            target_code_ids=[(6, 0, [self.code_ok.id])],
        )
        self._make_obs(
            self.type_coded, "2026-01-01 00:00:00", value_code_id=self.code_child.id
        )
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "in_range")

    def test_coded_value_matches_parent_of_target(self):
        goal = self._make_goal(
            self.type_coded,
            target_code_operator="parent_of",
            target_code_ids=[(6, 0, [self.code_child.id])],
        )
        self._make_obs(
            self.type_coded, "2026-01-01 00:00:00", value_code_id=self.code_ok.id
        )
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "in_range")

    # ── coded target: multi-value (code_ids) set semantics ─────────────────

    def test_coded_ids_equal_same_members_matches(self):
        goal = self._make_goal(
            self.type_coded_multi,
            target_code_operator="=",
            target_code_ids=[(6, 0, [self.code_x.id, self.code_y.id])],
        )
        self._make_obs(
            self.type_coded_multi,
            "2026-01-01 00:00:00",
            value_code_ids=[(6, 0, [self.code_y.id, self.code_x.id])],
        )
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "in_range")

    def test_coded_ids_equal_extra_member_does_not_match(self):
        goal = self._make_goal(
            self.type_coded_multi,
            target_code_operator="=",
            target_code_ids=[(6, 0, [self.code_x.id])],
        )
        self._make_obs(
            self.type_coded_multi,
            "2026-01-01 00:00:00",
            value_code_ids=[(6, 0, [self.code_x.id, self.code_y.id])],
        )
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "out_of_range")

    def test_coded_ids_in_subset_matches(self):
        goal = self._make_goal(
            self.type_coded_multi,
            target_code_operator="in",
            target_code_ids=[(6, 0, [self.code_x.id, self.code_y.id])],
        )
        self._make_obs(
            self.type_coded_multi,
            "2026-01-01 00:00:00",
            value_code_ids=[(6, 0, [self.code_x.id])],
        )
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "in_range")

    def test_coded_ids_in_member_outside_target_does_not_match(self):
        goal = self._make_goal(
            self.type_coded_multi,
            target_code_operator="in",
            target_code_ids=[(6, 0, [self.code_x.id])],
        )
        self._make_obs(
            self.type_coded_multi,
            "2026-01-01 00:00:00",
            value_code_ids=[(6, 0, [self.code_x.id, self.code_y.id])],
        )
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "out_of_range")

    def test_coded_ids_not_in_disjoint_matches(self):
        goal = self._make_goal(
            self.type_coded_multi,
            target_code_operator="not in",
            target_code_ids=[(6, 0, [self.code_x.id])],
        )
        self._make_obs(
            self.type_coded_multi,
            "2026-01-01 00:00:00",
            value_code_ids=[(6, 0, [self.code_y.id])],
        )
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "in_range")

    def test_coded_ids_not_in_overlap_does_not_match(self):
        goal = self._make_goal(
            self.type_coded_multi,
            target_code_operator="not in",
            target_code_ids=[(6, 0, [self.code_x.id])],
        )
        self._make_obs(
            self.type_coded_multi,
            "2026-01-01 00:00:00",
            value_code_ids=[(6, 0, [self.code_x.id, self.code_y.id])],
        )
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "out_of_range")

    def test_coded_ids_child_of_requires_all_members_to_match(self):
        goal = self._make_goal(
            self.type_coded_multi,
            target_code_operator="child_of",
            target_code_ids=[(6, 0, [self.code_ok.id])],
        )
        self._make_obs(
            self.type_coded_multi,
            "2026-01-01 00:00:00",
            value_code_ids=[(6, 0, [self.code_child.id, self.code_bad.id])],
        )
        goal.invalidate_recordset()

        self.assertEqual(
            goal.target_status,
            "out_of_range",
            "code_bad is not a descendant of code_ok, so not all members match",
        )

    def test_coded_ids_child_of_all_members_match(self):
        goal = self._make_goal(
            self.type_coded_multi,
            target_code_operator="child_of",
            target_code_ids=[(6, 0, [self.code_ok.id])],
        )
        self._make_obs(
            self.type_coded_multi,
            "2026-01-01 00:00:00",
            value_code_ids=[(6, 0, [self.code_child.id, self.code_ok.id])],
        )
        goal.invalidate_recordset()

        self.assertEqual(goal.target_status, "in_range")

    # ── alert messages ───────────────────────────────────────────────────

    def test_alert_no_baseline_yet(self):
        goal = self._make_goal(self.type_numeric, target_min=0, target_max=100)
        self._make_obs(self.type_numeric, "2026-01-01 00:00:00", value_float=50.0)
        goal.invalidate_recordset()

        self.assertFalse(goal.address_observation_id)
        self.assertIn("baseline", goal.target_alert_message)

    def test_alert_no_measurement_since_baseline(self):
        goal = self._make_goal(self.type_numeric, target_min=0, target_max=100)
        obs = self._make_obs(self.type_numeric, "2026-01-01 00:00:00", value_float=50.0)
        goal.invalidate_recordset()
        goal.write({"address_observation_id": obs.id})
        goal.invalidate_recordset()

        self.assertEqual(goal.observation_id, obs)
        self.assertIn("since the baseline", goal.target_alert_message)

    def test_no_alert_when_measured_after_baseline(self):
        goal = self._make_goal(self.type_numeric, target_min=0, target_max=100)
        baseline = self._make_obs(
            self.type_numeric, "2026-01-01 00:00:00", value_float=50.0
        )
        goal.invalidate_recordset()
        goal.write({"address_observation_id": baseline.id})
        self._make_obs(self.type_numeric, "2026-02-01 00:00:00", value_float=60.0)
        goal.invalidate_recordset()

        self.assertNotEqual(goal.observation_id, baseline)
        self.assertFalse(goal.target_alert_message)
