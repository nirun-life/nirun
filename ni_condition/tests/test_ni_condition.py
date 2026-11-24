#  Copyright (c) 2026 NSTDA
from psycopg2 import IntegrityError

from odoo.exceptions import UserError
from odoo.tools import mute_logger

from .common import ConditionCommon


class TestCondition(ConditionCommon):
    def test_display_name_context_keys(self):
        condition = self._create_condition(
            self.code_a, severity="mild", clinical_state="active"
        )

        def name(**context):
            return condition.with_context(**context).display_name

        self.assertEqual(name(), "Alpha Disease")
        self.assertEqual(name(show_code=True), "[Alpha Disease] T-ALPHA")
        self.assertEqual(
            name(show_patient=True), "Condition Test Patient: Alpha Disease"
        )
        self.assertEqual(name(show_severity=True), "Alpha Disease[Mild]")
        self.assertEqual(name(show_state=True), "Alpha Disease (Suffering)")
        self.assertEqual(
            name(
                show_code=True, show_patient=True, show_severity=True, show_state=True
            ),
            "Condition Test Patient: [Alpha Disease] T-ALPHA[Mild] (Suffering)",
        )

    def test_display_name_follows_the_record(self):
        condition = self._create_condition(self.code_a, severity="mild")
        shown = condition.with_context(show_severity=True)
        self.assertEqual(shown.display_name, "Alpha Disease[Mild]")
        condition.write({"severity": "severe", "name": "Renamed"})
        self.assertEqual(shown.display_name, "Renamed[Severe]")

    def test_code_display_name_context_keys(self):
        child = self._create_code(
            "Child Disease", "T-CHILD", "CD", parent_id=self.code_a.id
        )

        def name(**context):
            return child.with_context(**context).display_name

        self.assertEqual(name(), "Child Disease")
        self.assertEqual(name(show_parent=True), "Alpha Disease, Child Disease")
        self.assertEqual(name(show_abbr=True), "Child Disease (CD)")
        self.assertEqual(name(show_code=True), "T-CHILD  Child Disease")
        self.assertEqual(name(only_abbr=True), "CD")

    def test_verification_display_name(self):
        Verification = self.env["ni.condition.verification"]
        parent = Verification.create(
            {"name": "Parent", "code": "T-VP", "system_id": self.system.id}
        )
        child = Verification.create(
            {
                "name": "Child",
                "code": "T-VC",
                "system_id": self.system.id,
                "parent_id": parent.id,
            }
        )
        self.assertEqual(parent.display_name, "Parent")
        self.assertEqual(child.display_name, "Parent, Child")
        parent.name = "Renamed"
        self.assertEqual(child.display_name, "Renamed, Child")
        self.assertIn(
            (child.id, "Renamed, Child"), Verification.name_search("T-VC", limit=None)
        )

    def test_one_condition_per_patient_and_code(self):
        self._create_condition(self.code_a)
        self._create_condition(self.code_b)
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self._create_condition(self.code_a)

    def test_category_flags(self):
        condition = self._create_condition(self.code_a, is_problem=True)
        self.assertEqual(
            condition.category_ids, self.env.ref("ni_condition.problem_list_item")
        )
        self.assertTrue(condition.is_problem)
        self.assertFalse(condition.is_diagnosis)

    def test_hierarchy(self):
        for model in (
            "ni.condition.category",
            "ni.condition.code",
            "ni.condition.verification",
            "ni.encounter.diagnosis.role",
        ):
            with self.subTest(model=model):
                vals = {"system_id": self.system.id}
                root = self.env[model].create(
                    {"name": "T Root", "code": "T-H-ROOT", **vals}
                )
                child = self.env[model].create(
                    {
                        "name": "T Child",
                        "code": "T-H-CHILD",
                        "parent_id": root.id,
                        **vals,
                    }
                )
                self.assertEqual(child.parent_id, root)
                # ValidationError of the constraint, or UserError of _parent_store
                with self.assertRaises(UserError), self.env.cr.savepoint():
                    root.parent_id = child
                    root.flush_recordset()

    def test_observation_of_the_code(self):
        obs_type = self.env["ni.observation.type"].create(
            {
                "name": "Condition Test",
                "code": "test-condition",
                "value_type": "int",
                "min": 0,
                "max": 100,
            }
        )
        self.code_a.observation_code_ids = obs_type
        condition = self._create_condition(self.code_a)
        self.assertEqual(condition.observation_count, 0)
        encounter = self._create_encounter()
        observation = self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": encounter.id,
                "type_id": obs_type.id,
                "occurrence": "2025-01-01 08:00:00",
                "value_int": 5,
            }
        )
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertEqual(condition.observation_count, 1)
        self.assertEqual(condition.observation_ids.ids, observation.ids)
        self.assertEqual(self.code_a.observation_code_count, 1)
