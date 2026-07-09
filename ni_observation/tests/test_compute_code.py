#  Copyright (c) 2026 NSTDA

from odoo import fields
from odoo.tests import common


class TestComputeCode(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "Compute Test Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})

        # ── float input types ──────────────────────────────────────────────────
        cls.type_a = cls.env["ni.observation.type"].create(
            {
                "name": "Input A",
                "code": "test-input-a",
                "value_type": "float",
                "min": 0,
                "max": 9999,
            }
        )
        cls.type_b = cls.env["ni.observation.type"].create(
            {
                "name": "Input B",
                "code": "test-input-b",
                "value_type": "float",
                "min": 0,
                "max": 9999,
            }
        )

        # Computed float — components linked via child_ids
        cls.type_sum = cls.env["ni.observation.type"].create(
            {
                "name": "Sum AB",
                "code": "test-sum-ab",
                "value_type": "float",
                "compute": True,
                "compute_code": "result = test_input_a + test_input_b",
                "child_ids": [(4, cls.type_a.id), (4, cls.type_b.id)],
                "min": 0,
                "max": 99999,
            }
        )

        # ── int input types for char output ────────────────────────────────────
        cls.type_x = cls.env["ni.observation.type"].create(
            {
                "name": "Input X",
                "code": "test-input-x",
                "value_type": "int",
                "min": 0,
                "max": 9999,
            }
        )
        cls.type_y = cls.env["ni.observation.type"].create(
            {
                "name": "Input Y",
                "code": "test-input-y",
                "value_type": "int",
                "min": 0,
                "max": 9999,
            }
        )

        # Computed char — same pattern as Blood Pressure
        cls.type_pair = cls.env["ni.observation.type"].create(
            {
                "name": "Pair XY",
                "code": "test-pair-xy",
                "value_type": "char",
                "compute": True,
                "compute_code": "result = '{} / {}'.format(test_input_x, test_input_y) if test_input_x and test_input_y else None",
                "child_ids": [(4, cls.type_x.id), (4, cls.type_y.id)],
            }
        )

    # ── helpers ────────────────────────────────────────────────────────────────

    def _make_sheet(self):
        return self.env["ni.observation.sheet"].create(
            {"patient_id": self.patient.id, "occurrence": fields.Datetime.now()}
        )

    def _add_obs(self, sheet, ob_type, value):
        ob = self.env["ni.observation"].create(
            {
                "sheet_id": sheet.id,
                "type_id": ob_type.id,
                "patient_id": sheet.patient_id.id,
                "occurrence": sheet.occurrence,
            }
        )
        ob.value = str(value)
        return ob

    def _get_computed(self, sheet, ob_type):
        return sheet.observation_ids.filtered(lambda o: o.type_id == ob_type)

    # ── float result ───────────────────────────────────────────────────────────

    def test_float_computed_on_create(self):
        sheet = self._make_sheet()
        self._add_obs(sheet, self.type_a, 10)
        self._add_obs(sheet, self.type_b, 20)

        ob = self._get_computed(sheet, self.type_sum)
        self.assertTrue(ob, "computed obs should be auto-created")
        self.assertAlmostEqual(ob.value_float, 30.0)

    def test_float_computed_updates_when_input_changes(self):
        sheet = self._make_sheet()
        ob_a = self._add_obs(sheet, self.type_a, 10)
        self._add_obs(sheet, self.type_b, 20)

        ob_a.value = "15"

        ob = self._get_computed(sheet, self.type_sum)
        self.assertAlmostEqual(ob.value_float, 35.0)

    # ── char result ────────────────────────────────────────────────────────────

    def test_char_computed_on_create(self):
        sheet = self._make_sheet()
        self._add_obs(sheet, self.type_x, 120)
        self._add_obs(sheet, self.type_y, 80)

        ob = self._get_computed(sheet, self.type_pair)
        self.assertTrue(ob)
        self.assertEqual(ob.value_char, "120 / 80")

    def test_char_computed_updates_when_input_changes(self):
        sheet = self._make_sheet()
        ob_x = self._add_obs(sheet, self.type_x, 120)
        self._add_obs(sheet, self.type_y, 80)

        ob_x.value = "130"

        ob = self._get_computed(sheet, self.type_pair)
        self.assertEqual(ob.value_char, "130 / 80")

    # ── idempotency ────────────────────────────────────────────────────────────

    def test_no_duplicate_computed_obs_on_repeated_writes(self):
        sheet = self._make_sheet()
        self._add_obs(sheet, self.type_a, 10)
        ob_b = self._add_obs(sheet, self.type_b, 20)

        ob_b.value = "25"
        ob_b.value = "30"

        computed = self._get_computed(sheet, self.type_sum)
        self.assertEqual(len(computed), 1, "must not duplicate computed observations")
        self.assertAlmostEqual(computed.value_float, 40.0)

    # ── skip conditions ────────────────────────────────────────────────────────

    def test_no_computed_obs_when_inputs_are_empty(self):
        sheet = self._make_sheet()
        for t in (self.type_a, self.type_b):
            self.env["ni.observation"].create(
                {
                    "sheet_id": sheet.id,
                    "type_id": t.id,
                    "patient_id": self.patient.id,
                    "occurrence": sheet.occurrence,
                }
            )

        ob = self._get_computed(sheet, self.type_sum)
        self.assertFalse(
            ob, "should not create computed obs when all inputs have no value"
        )

    def test_code_returning_none_does_not_create_obs(self):
        inp = self.env["ni.observation.type"].create(
            {
                "name": "None Input",
                "code": "test-none-inp",
                "value_type": "float",
                "min": 0,
                "max": 9999,
            }
        )
        none_type = self.env["ni.observation.type"].create(
            {
                "name": "None Result",
                "code": "test-none-result",
                "value_type": "float",
                "compute": True,
                "compute_code": "result = None",
                "child_ids": [(4, inp.id)],
                "min": 0,
                "max": 9999,
            }
        )
        sheet = self._make_sheet()
        self._add_obs(sheet, inp, 5)

        ob = self._get_computed(sheet, none_type)
        self.assertFalse(ob)

    def test_code_not_assigning_result_does_not_create_obs(self):
        inp = self.env["ni.observation.type"].create(
            {
                "name": "No-Assign Input",
                "code": "test-noassign-inp",
                "value_type": "float",
                "min": 0,
                "max": 9999,
            }
        )
        no_assign_type = self.env["ni.observation.type"].create(
            {
                "name": "No Assign",
                "code": "test-no-assign",
                "value_type": "float",
                "compute": True,
                "compute_code": "x = test_noassign_inp * 2",  # never sets result
                "child_ids": [(4, inp.id)],
                "min": 0,
                "max": 9999,
            }
        )
        sheet = self._make_sheet()
        self._add_obs(sheet, inp, 5)

        ob = self._get_computed(sheet, no_assign_type)
        self.assertFalse(ob)

    # ── error safety ───────────────────────────────────────────────────────────

    def test_code_exception_does_not_crash_write(self):
        inp = self.env["ni.observation.type"].create(
            {
                "name": "Bad Input",
                "code": "test-bad-inp",
                "value_type": "float",
                "min": 0,
                "max": 9999,
            }
        )
        bad_type = self.env["ni.observation.type"].create(
            {
                "name": "Bad Code",
                "code": "test-bad-code",
                "value_type": "float",
                "compute": True,
                "compute_code": "result = 1 / 0",
                "child_ids": [(4, inp.id)],
                "min": 0,
                "max": 9999,
            }
        )
        sheet = self._make_sheet()
        self._add_obs(sheet, inp, 5)  # must not raise

        ob = self._get_computed(sheet, bad_type)
        self.assertFalse(ob, "failed compute should not create any observation")

    # ── input linkage ─────────────────────────────────────────────────────────

    def test_computed_obs_links_input_observations_as_children(self):
        sheet = self._make_sheet()
        ob_a = self._add_obs(sheet, self.type_a, 10)
        ob_b = self._add_obs(sheet, self.type_b, 20)

        computed = self._get_computed(sheet, self.type_sum)
        self.assertIn(ob_a, computed.child_ids)
        self.assertIn(ob_b, computed.child_ids)

    def test_input_obs_parent_points_to_computed_obs(self):
        sheet = self._make_sheet()
        ob_a = self._add_obs(sheet, self.type_a, 10)
        ob_b = self._add_obs(sheet, self.type_b, 20)

        computed = self._get_computed(sheet, self.type_sum)
        self.assertEqual(ob_a.parent_id, computed)
        self.assertEqual(ob_b.parent_id, computed)

    def test_workflow_event_parent_matches_observation_parent(self):
        # regression: WorkflowMixin._to_workflow() used to write the parent
        # ni.observation's own id into ni.workflow.event.parent_id (which
        # only accepts other ni.workflow.event ids), raising a foreign key
        # violation once both child values were set and the computed parent
        # observation got linked via child_ids.
        sheet = self._make_sheet()
        ob_a = self._add_obs(sheet, self.type_a, 10)
        ob_b = self._add_obs(sheet, self.type_b, 20)

        computed = self._get_computed(sheet, self.type_sum)
        self.assertEqual(ob_a.event_id.parent_id, computed.event_id)
        self.assertEqual(ob_b.event_id.parent_id, computed.event_id)

    def test_child_ids_updated_when_input_value_changes(self):
        sheet = self._make_sheet()
        ob_a = self._add_obs(sheet, self.type_a, 10)
        ob_b = self._add_obs(sheet, self.type_b, 20)
        ob_a.value = "15"

        computed = self._get_computed(sheet, self.type_sum)
        self.assertIn(ob_a, computed.child_ids)
        self.assertIn(ob_b, computed.child_ids)
        self.assertEqual(len(computed.child_ids), 2)

    # ── seeded types ───────────────────────────────────────────────────────────

    def test_seeded_bp_computes_from_systolic_and_diastolic(self):
        type_bp = self.env.ref("ni_observation.type_bp")
        type_bp_s = self.env.ref("ni_observation.type_bp_s")
        type_bp_d = self.env.ref("ni_observation.type_bp_d")

        if not type_bp.compute_code:
            self.skipTest("type_bp.compute_code not seeded (existing database)")

        sheet = self._make_sheet()
        self._add_obs(sheet, type_bp_s, 120)
        self._add_obs(sheet, type_bp_d, 80)

        ob = self._get_computed(sheet, type_bp)
        self.assertTrue(ob, "BP observation should be auto-created")
        self.assertEqual(ob.value_char, "120 / 80")

    def test_seeded_bmi_computes_from_weight_and_height(self):
        type_bmi = self.env.ref("ni_observation.type_bmi")
        type_weight = self.env.ref("ni_observation.type_body_weight")
        type_height = self.env.ref("ni_observation.type_body_height")

        if not type_bmi.compute_code:
            self.skipTest("type_bmi.compute_code not seeded (existing database)")

        sheet = self._make_sheet()
        self._add_obs(sheet, type_weight, 70)  # 70 kg
        self._add_obs(sheet, type_height, 170)  # 170 cm

        ob = self._get_computed(sheet, type_bmi)
        self.assertTrue(ob, "BMI observation should be auto-created")
        expected = round(70 / (170 * 0.01) ** 2, 1)  # 24.2
        self.assertAlmostEqual(ob.value_float, expected, places=1)
