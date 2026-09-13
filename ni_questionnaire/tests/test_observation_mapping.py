#  Copyright (c) 2026 NSTDA
"""How a completed response turns into observations.

Covers the three producers in `survey.user_input._create_survey_observations` --
the whole-survey score, a single answer, and a question group -- plus the guards
that stop a misconfigured questionnaire from writing nonsense.
"""

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import common


class TestObservationMapping(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "Mapping Test Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})

        cls.int_type = cls._obs_type("Total", "test-map-total", "int")
        cls.float_type = cls._obs_type("Percent", "test-map-pct", "float")
        cls.char_type = cls._obs_type("Free Text", "test-map-char", "char")
        cls.item_type = cls._obs_type("Item", "test-map-item", "int")

        cls.survey = cls.env["survey.survey"].create(
            {
                "title": "Observation Mapping",
                "scoring_type": "scoring_without_answers",
                "subject_type": "ni.patient",
            }
        )
        cls.q_six = cls._choice_question("Worth 6", 10, 6)
        cls.q_four = cls._choice_question("Worth 4", 20, 4)

    # ------------------------------------------------------------------ fixtures

    @classmethod
    def _obs_type(cls, name, code, value_type, **kwargs):
        vals = {
            "name": name,
            "code": code,
            "value_type": value_type,
            "min": 0,
            "max": 100,
        }
        vals.update(kwargs)
        return cls.env["ni.observation.type"].create(vals)

    @classmethod
    def _choice_question(cls, title, sequence, score, **kwargs):
        vals = {
            "title": title,
            "sequence": sequence,
            "survey_id": cls.survey.id,
            "question_type": "simple_choice",
            "suggested_answer_ids": [
                (0, 0, {"value": "No", "answer_score": 0}),
                (0, 0, {"value": "Yes", "answer_score": score}),
            ],
        }
        vals.update(kwargs)
        return cls.env["survey.question"].create(vals)

    def _question(self, question_type, **kwargs):
        vals = {
            "title": "Open %s" % question_type,
            "sequence": 30,
            "survey_id": self.survey.id,
            "question_type": question_type,
        }
        vals.update(kwargs)
        return self.env["survey.question"].create(vals)

    def _response(self):
        return self.env["survey.user_input"].create(
            {
                "survey_id": self.survey.id,
                "patient_id": self.patient.id,
                "subject_model": "ni.patient",
                "subject_id": self.patient.id,
            }
        )

    def _choose(self, response, question, value):
        answer = question.suggested_answer_ids.filtered(lambda a: a.value == value)
        return self.env["survey.user_input.line"].create(
            {
                "user_input_id": response.id,
                "survey_id": self.survey.id,
                "question_id": question.id,
                "skipped": False,
                "answer_type": "suggestion",
                "suggested_answer_id": answer.id,
            }
        )

    def _answer(self, response, question, answer_type, **value):
        vals = {
            "user_input_id": response.id,
            "survey_id": self.survey.id,
            "question_id": question.id,
            "skipped": False,
            "answer_type": answer_type,
        }
        vals.update(value)
        return self.env["survey.user_input.line"].create(vals)

    def _observations(self, response):
        return self.env["ni.observation"].search(
            [("survey_response_id", "=", response.id)]
        )

    def _scored_response(self):
        """6 of 10 points."""
        response = self._response()
        self._choose(response, self.q_six, "Yes")
        self._choose(response, self.q_four, "No")
        return response

    # ------------------------------------------------------- whole-survey score

    def test_raw_score_observation_records_the_total(self):
        self.survey.write(
            {"observation_type_id": self.int_type.id, "observation_score_type": "raw"}
        )
        response = self._scored_response()
        response._mark_done()

        observation = self._observations(response)
        self.assertEqual(observation.type_id, self.int_type)
        self.assertEqual(observation.value_int, 6)

    def test_percentage_score_observation_records_the_percentage(self):
        self.survey.write(
            {
                "observation_type_id": self.float_type.id,
                "observation_score_type": "percentage",
            }
        )
        response = self._scored_response()
        response._mark_done()

        self.assertEqual(self._observations(response).value_float, 60.0)

    def test_int_observation_truncates_a_fractional_score(self):
        """60% into an integer observation is 60, not a crash."""
        self.survey.write(
            {
                "observation_type_id": self.int_type.id,
                "observation_score_type": "percentage",
            }
        )
        self.q_six.suggested_answer_ids.filtered(
            lambda a: a.value == "Yes"
        ).answer_score = 6.5
        response = self._scored_response()
        response._mark_done()

        self.assertEqual(self._observations(response).value_int, 61)

    def test_score_needs_a_numeric_observation_type(self):
        """The type may be made non-numeric after the survey was wired to it."""
        self.survey.observation_type_id = self.int_type
        response = self._scored_response()
        self.int_type.value_type = "char"
        with self.assertRaises(ValidationError):
            response._mark_done()

    # ------------------------------------------------------------ single answer

    def test_question_without_a_code_produces_nothing(self):
        response = self._scored_response()
        response._mark_done()
        self.assertFalse(self._observations(response))

    def test_score_answer_records_the_answer_score(self):
        self.q_six.write(
            {
                "observation_code_id": self.item_type.id,
                "observation_answer_type": "score",
            }
        )
        response = self._scored_response()
        response._mark_done()

        observation = self._observations(response)
        self.assertEqual(observation.type_id, self.item_type)
        self.assertEqual(observation.value_int, 6)

    def test_value_answer_records_the_chosen_answer_text(self):
        self.q_six.write(
            {
                "observation_code_id": self.char_type.id,
                "observation_answer_type": "value",
            }
        )
        response = self._scored_response()
        response._mark_done()

        self.assertEqual(self._observations(response).value_char, "Yes")

    def test_numerical_answer_of_zero_is_a_real_answer(self):
        """Zero must not be mistaken for "no answer given"."""
        question = self._question(
            "numerical_box",
            observation_code_id=self.int_type.id,
            observation_answer_type="value",
        )
        response = self._response()
        self._answer(response, question, "numerical_box", value_numerical_box=0)
        response._mark_done()

        self.assertEqual(self._observations(response).value_int, 0)

    def test_datetime_answer_is_recorded(self):
        question = self._question(
            "datetime",
            observation_code_id=self.char_type.id,
            observation_answer_type="value",
        )
        moment = fields.Datetime.to_datetime("2026-01-02 03:04:05")
        response = self._response()
        self._answer(response, question, "datetime", value_datetime=moment)
        response._mark_done()

        self.assertEqual(self._observations(response).value_char, str(moment))

    # ----------------------------------------------------------- question group

    def _group(self, operator, questions=None):
        return self.env["survey.question.group"].create(
            {
                "survey_id": self.survey.id,
                "operator": operator,
                "question_ids": [(6, 0, (questions or (self.q_six | self.q_four)).ids)],
                "observation_code_id": self.item_type.id,
            }
        )

    def test_group_operators_aggregate_the_answer_scores(self):
        """Answers worth 6 and 4."""
        for operator, expected in [("sum", 10), ("avg", 5), ("min", 4), ("max", 6)]:
            with self.subTest(operator=operator):
                group = self._group(operator)
                response = self._response()
                self._choose(response, self.q_six, "Yes")
                self._choose(response, self.q_four, "Yes")
                response._mark_done()

                self.assertEqual(self._observations(response).value_int, expected)
                group.unlink()

    def test_group_with_no_answered_question_produces_nothing(self):
        other = self._choice_question("Unanswered A", 40, 3)
        another = self._choice_question("Unanswered B", 50, 3)
        self._group("avg", other | another)

        response = self._scored_response()
        response._mark_done()

        self.assertFalse(self._observations(response))

    # --------------------------------------------------------- grade selection

    def test_grade_for_narrows_to_the_patient_demographics(self):
        survey = self.survey
        any_one = self.env["survey.grade"].create(
            {"survey_id": survey.id, "name": "Any", "low": 0, "high": 100}
        )
        elderly = self.env["survey.grade"].create(
            {"survey_id": survey.id, "name": "Elderly", "age_low": 60, "age_high": 200}
        )
        women = self.env["survey.grade"].create(
            {"survey_id": survey.id, "name": "Women", "gender": "female"}
        )

        grades = any_one | elderly | women
        self.assertEqual(grades.grade_for(age=30, gender="male"), any_one)
        self.assertEqual(grades.grade_for(age=70, gender="male"), any_one | elderly)
        self.assertEqual(grades.grade_for(age=30, gender="female"), any_one | women)

    # -------------------------------------------------- cloning reference ranges

    def _with_reference_ranges(self):
        interpretation = self.env["ni.observation.interpretation"].create(
            {"name": "Map High", "code": "test-map-H", "display_class": "danger"}
        )
        self.env["ni.observation.reference.range"].create(
            {
                "type_id": self.int_type.id,
                "low": 0,
                "high": 50,
                "interpretation_id": interpretation.id,
            }
        )
        self.survey.observation_type_id = self.int_type
        return interpretation

    def test_cloning_ranges_scales_to_percent_under_the_percentage_basis(self):
        interpretation = self._with_reference_ranges()
        self.survey.grading_basis = "percentage"
        self.survey.action_sync_observation_range()

        grade = self.survey.grade_ids
        self.assertEqual(len(grade), 1)
        self.assertEqual((grade.low, grade.high), (0.0, 50.0))
        self.assertEqual(grade.interpretation_id, interpretation)

    def test_cloning_ranges_keeps_raw_bounds_under_the_score_basis(self):
        """Points grades are compared with scoring_total, so 50 must stay 50."""
        self._with_reference_ranges()
        self.survey.grading_basis = "score"
        self.int_type.max = 20
        self.survey.action_sync_observation_range()

        grade = self.survey.grade_ids
        self.assertEqual((grade.low, grade.high), (0.0, 50.0))

    def test_cloning_ranges_replaces_the_existing_grades(self):
        self._with_reference_ranges()
        self.env["survey.grade"].create(
            {"survey_id": self.survey.id, "name": "Stale", "low": 0, "high": 100}
        )
        self.survey.action_sync_observation_range()

        self.assertEqual(self.survey.grade_ids.mapped("name"), ["Map High"])

    def test_cloning_ranges_needs_an_observation_type_with_ranges(self):
        with self.assertRaises(ValidationError):
            self.survey.action_sync_observation_range()

        self.survey.observation_type_id = self.int_type
        with self.assertRaises(ValidationError):
            self.survey.action_sync_observation_range()

    # -------------------------------------------------------------- consistency

    def test_response_encounter_must_belong_to_its_patient(self):
        other_partner = self.env["res.partner"].create({"name": "Someone Else"})
        other_patient = self.env["ni.patient"].create({"partner_id": other_partner.id})
        encounter_class = self.env["ni.encounter.class"].create(
            {"name": "Mapping Test Class"}
        )
        encounter = self.env["ni.encounter"].create(
            {"patient_id": other_patient.id, "class_id": encounter_class.id}
        )

        response = self._response()
        with self.assertRaises(ValidationError):
            response.encounter_id = encounter

    def test_group_needs_at_least_two_questions(self):
        with self.assertRaises(UserError):
            self._group("sum", self.q_six)

    def test_survey_observation_type_must_be_numeric(self):
        with self.assertRaises(UserError):
            self.survey.observation_type_id = self._obs_type(
                "Coded", "test-map-coded", "code_id"
            )
