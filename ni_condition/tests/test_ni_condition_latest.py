#  Copyright (c) 2026 NSTDA
from .common import ConditionCommon


class TestConditionLatest(ConditionCommon):
    def _latest(self, patient=None):
        self.env.flush_all()
        self.env.invalidate_all()
        return self.env["ni.condition.latest"].search(
            [("patient_id", "=", (patient or self.patient).id)]
        )

    def test_state_filter(self):
        expected = self.env["ni.condition"]
        for index, (state, shown) in enumerate(
            [
                ("active", True),
                ("recurrence", True),
                ("remission", True),
                ("relapse", False),
                ("inactive", False),
                ("resolved", False),
            ]
        ):
            code = self._create_code(f"State {state}", f"T-S{index}")
            condition = self._create_condition(code, clinical_state=state)
            if shown:
                expected |= condition
        self.assertEqual(set(self._latest().ids), set(expected.ids))

    def test_one_row_per_patient_and_code(self):
        """Free-text conditions have no code: they are one group per patient, and
        the newest record of the group with a shown state is the latest."""
        coded = self._create_condition(self.code_a)
        self._create_condition(name="Free 1")
        last = self._create_condition(name="Free 2", clinical_state="remission")
        self._create_condition(name="Free 3", clinical_state="inactive")
        other = self._create_patient("Condition Other Patient")
        other_condition = self._create_condition(self.code_a, patient_id=other.id)
        self.assertEqual(set(self._latest().ids), set((coded | last).ids))
        self.assertEqual(self._latest(other).ids, other_condition.ids)

    def test_row_values(self):
        encounter = self._create_encounter()
        condition = self._create_condition(
            self.code_a,
            encounter_id=encounter.id,
            severity="severe",
            period_start="2025-01-02 03:00:00",
            note="Latest note",
        )
        row = self._latest()
        self.assertEqual(row.id, condition.id)
        self.assertEqual(row.company_id, condition.company_id)
        self.assertEqual(row.encounter_id, encounter)
        self.assertEqual(row.code_id, self.code_a)
        self.assertEqual(row.clinical_state, "active")
        self.assertEqual(row.severity, "severe")
        self.assertEqual(str(row.period_start), "2025-01-02 03:00:00")
        self.assertEqual(row.display_name, "Alpha Disease")
        self.assertEqual(self.patient.condition_report_ids.ids, condition.ids)

    def test_search_by_code(self):
        """ni_medication looks up the latest conditions by code."""
        condition = self._create_condition(self.code_a)
        self._create_condition(self.code_b)
        self.env.flush_all()
        found = self.env["ni.condition.latest"].search(
            [("code_id", "in", self.code_a.ids), ("patient_id", "=", self.patient.id)]
        )
        self.assertEqual(found.ids, condition.ids)
