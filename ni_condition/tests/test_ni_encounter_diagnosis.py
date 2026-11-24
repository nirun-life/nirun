#  Copyright (c) 2026 NSTDA
from odoo.exceptions import UserError, ValidationError

from .common import ConditionCommon


class TestEncounterDiagnosis(ConditionCommon):
    def test_diagnosis_count(self):
        first = self._create_encounter()
        other_patient = self._create_patient("Diagnosis Other Patient")
        second = self._create_encounter(other_patient)
        self._create_diagnosis(first, self.code_a, self.role_chief)
        self._create_diagnosis(first, self.code_b, self.role_other)
        self._create_diagnosis(second, self.code_a, self.role_chief)
        third = self._create_encounter(self._create_patient("Diagnosis Third"))
        encounters = first | second | third
        encounters.invalidate_recordset()
        self.assertEqual(encounters.mapped("diagnosis_count"), [2, 1, 0])

    def test_role_limit(self):
        self.assertEqual(self.role_chief.limit, 1)
        encounter = self._create_encounter()
        self._create_diagnosis(encounter, self.code_a, self.role_chief)
        with self.assertRaises(ValidationError):
            encounter.write(
                {
                    "diagnosis_ids": [
                        (
                            0,
                            0,
                            {
                                "patient_id": self.patient.id,
                                "name": self.code_b.name,
                                "code_id": self.code_b.id,
                                "role_id": self.role_chief.id,
                                "is_diagnosis": True,
                            },
                        )
                    ]
                }
            )

    def test_diagnosis_needs_a_role(self):
        encounter = self._create_encounter()
        with self.assertRaises(UserError):
            self._create_diagnosis(
                encounter, self.code_a, self.env["ni.encounter.diagnosis.role"]
            )

    def test_reuses_the_condition_of_the_patient(self):
        condition = self._create_condition(self.code_a, is_problem=True)
        encounter = self._create_encounter()
        diagnosis = self._create_diagnosis(encounter, self.code_a, self.role_chief)
        self.assertEqual(diagnosis.condition_id, condition)
        self.assertTrue(diagnosis.is_problem)

    def test_confirm_copies_the_problem_list(self):
        problem = self._create_condition(self.code_a, is_problem=True)
        self._create_condition(self.code_b)
        encounter = self._create_encounter()
        self.assertFalse(encounter.diagnosis_ids)
        encounter.action_confirm()
        self.assertEqual(encounter.diagnosis_ids.condition_id, problem)
        self.assertTrue(encounter.diagnosis_ids.is_problem)

    def test_toggle_diagnosis(self):
        problem = self._create_condition(self.code_a, is_problem=True)
        encounter = self._create_encounter()
        encounter.action_confirm()
        line = encounter.diagnosis_ids
        self.assertEqual(line.condition_id, problem)
        action = line.action_toggle_is_diagnosis()
        self.assertEqual(action["res_model"], "ni.encounter.diagnosis.role.wizard")
        wizard = self.env[action["res_model"]].create(
            {"diagnosis_id": line.id, "role_id": self.role_chief.id}
        )
        wizard.action_confirm()
        self.assertTrue(line.is_diagnosis)
        self.assertEqual(line.role_id, self.role_chief)
        line.action_toggle_is_diagnosis()
        self.assertFalse(line.is_diagnosis)
        self.assertFalse(line.role_id)
