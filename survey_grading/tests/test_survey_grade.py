#  Copyright (c) 2026 NSTDA
"""`survey.grade` under both grading bases.

Every survey here is scored out of 10 by two questions worth 6 and 4 points, so a
response worth 6 points sits at 60%. The band sets are chosen to disagree on that
response: under `percentage` 60 fails, under `score` 6 passes.
"""

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestSurveyGrade(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.percentage_survey = cls._survey("Percentage Basis", "percentage")
        cls._grade(cls.percentage_survey, "Fail", 0, 70)
        cls._grade(cls.percentage_survey, "Pass", 71, 100)

        cls.score_survey = cls._survey("Points Basis", "score")
        cls._grade(cls.score_survey, "Fail", 0, 5)
        cls._grade(cls.score_survey, "Pass", 6, 10)

    # ------------------------------------------------------------------ helpers

    @classmethod
    def _survey(cls, title, grading_basis):
        survey = cls.env["survey.survey"].create(
            {
                "title": title,
                "scoring_type": "scoring_without_answers",
                "grading_basis": grading_basis,
            }
        )
        cls._question(survey, "Worth 6", 10, 6)
        cls._question(survey, "Worth 4", 20, 4)
        return survey

    @classmethod
    def _question(cls, survey, title, sequence, score):
        return cls.env["survey.question"].create(
            {
                "title": title,
                "sequence": sequence,
                "survey_id": survey.id,
                "question_type": "simple_choice",
                "suggested_answer_ids": [
                    (0, 0, {"value": "No", "answer_score": 0}),
                    (0, 0, {"value": "Yes", "answer_score": score}),
                ],
            }
        )

    @classmethod
    def _grade(cls, survey, name, low, high, answers=None):
        return cls.env["survey.grade"].create(
            {
                "survey_id": survey.id,
                "name": name,
                "low": low,
                "high": high,
                "triggering_answer_ids": [(6, 0, answers.ids if answers else [])],
            }
        )

    def _respond(self, survey, *picks):
        """Answer every question, choosing "Yes" only for the questions in picks."""
        response = self.env["survey.user_input"].create({"survey_id": survey.id})
        for question in survey.question_ids:
            value = "Yes" if question in picks else "No"
            answer = question.suggested_answer_ids.filtered(
                lambda a, v=value: a.value == v
            )
            self.env["survey.user_input.line"].create(
                {
                    "user_input_id": response.id,
                    "survey_id": survey.id,
                    "question_id": question.id,
                    "skipped": False,
                    "answer_type": "suggestion",
                    "suggested_answer_id": answer.id,
                }
            )
        response._mark_done()
        return response

    def _question_worth(self, survey, score):
        return survey.question_ids.filtered(
            lambda q, s=score: s in q.suggested_answer_ids.mapped("answer_score")
        )

    # ------------------------------------------------------ the two grading bases

    def test_percentage_basis_grades_on_scoring_percentage(self):
        response = self._respond(
            self.percentage_survey, self._question_worth(self.percentage_survey, 6)
        )
        self.assertEqual(response._grading_value(), 60.0)
        self.assertEqual(response.scoring_total, 6)
        self.assertEqual(response.grade_id.name, "Fail")

    def test_score_basis_grades_on_scoring_total(self):
        """Same 6-of-10 response, opposite grade, because the basis differs."""
        response = self._respond(
            self.score_survey, self._question_worth(self.score_survey, 6)
        )
        self.assertEqual(response._grading_value(), 6.0)
        self.assertEqual(response.scoring_percentage, 60.0)
        self.assertEqual(response.grade_id.name, "Pass")

    def test_changing_the_basis_regrades_existing_responses(self):
        response = self._respond(
            self.percentage_survey, self._question_worth(self.percentage_survey, 6)
        )
        self.assertEqual(response.grade_id.name, "Fail")

        self.percentage_survey.grade_ids.unlink()
        self.percentage_survey.grading_basis = "score"
        self._grade(self.percentage_survey, "Fail", 0, 5)
        self._grade(self.percentage_survey, "Pass", 6, 10)

        self.assertEqual(response.grade_id.name, "Pass")

    # ------------------------------------------------------- the completion page

    def _completion_page(self, response):
        return str(
            self.env["ir.qweb"]._render(
                "survey.survey_fill_form_done",
                {"survey": response.survey_id, "answer": response, "graph_data": False},
            )
        )

    def test_finished_page_shows_the_badge_without_a_passing_mark(self):
        """Core gates the score block on scoring_success_min, which a points
        questionnaire leaves at 0; the badge must not go down with it."""
        self.score_survey.scoring_success_min = 0
        self.score_survey.grade_ids.filtered(lambda g: g.name == "Pass").name = "Badge"
        response = self._respond(
            self.score_survey, self._question_worth(self.score_survey, 6)
        )
        self.assertEqual(response.grade_id.name, "Badge")
        self.assertIn("Badge", self._completion_page(response))

    def test_no_verdict_without_a_passing_mark(self):
        """scoring_success is trivially true at scoring_success_min 0, so neither
        branch of the passed/failed verdict may render."""
        self.score_survey.scoring_success_min = 0
        response = self._respond(
            self.score_survey, self._question_worth(self.score_survey, 6)
        )
        self.assertTrue(response.scoring_success)

        page = self._completion_page(response)
        self.assertNotIn("you have passed the test", page)
        self.assertNotIn("you have failed the test", page)

    def test_verdict_is_untouched_when_there_is_a_passing_mark(self):
        self.percentage_survey.scoring_success_min = 50
        passed = self._respond(
            self.percentage_survey, self._question_worth(self.percentage_survey, 6)
        )
        self.assertIn("you have passed the test", self._completion_page(passed))

        failed = self._respond(self.percentage_survey)
        self.assertIn("you have failed the test", self._completion_page(failed))

    def test_percentage_basis_rejects_ranges_outside_0_100(self):
        with self.assertRaises(ValidationError):
            self._grade(self.percentage_survey, "Impossible", 0, 150)

    def test_score_basis_allows_ranges_above_100(self):
        """A points questionnaire may be scored out of anything."""
        grade = self._grade(self.score_survey, "Long Form", 101, 250)
        self.assertTrue(grade.is_cover(200))

    def test_passing_grade_is_percentage_only(self):
        self.percentage_survey.scoring_success_min = 71.0
        percentage_pass = self.percentage_survey.grade_ids.filtered(
            lambda g: g.name == "Pass"
        )
        self.assertTrue(percentage_pass.passing_grade)

        # scoring_success_min is a percentage, so it says nothing about raw points
        self.score_survey.scoring_success_min = 6.0
        score_pass = self.score_survey.grade_ids.filtered(lambda g: g.name == "Pass")
        self.assertFalse(score_pass.passing_grade)

    def test_is_cover_includes_both_bounds(self):
        grade = self.score_survey.grade_ids.filtered(lambda g: g.name == "Pass")
        self.assertTrue(grade.is_cover(6))
        self.assertTrue(grade.is_cover(10))
        self.assertFalse(grade.is_cover(5.99))
        self.assertFalse(grade.is_cover(10.01))

    # ------------------------------------------------------------ answer scoping

    def test_answer_scoped_grades_take_precedence(self):
        """An unscoped set is the fallback, not a competitor."""
        gate = self._question_worth(self.score_survey, 4)
        yes = gate.suggested_answer_ids.filtered(lambda a: a.value == "Yes")
        self._grade(self.score_survey, "Scoped Fail", 0, 9, yes)
        self._grade(self.score_survey, "Scoped Pass", 10, 10, yes)

        without_gate = self._respond(
            self.score_survey, self._question_worth(self.score_survey, 6)
        )
        with_gate = self._respond(self.score_survey, *self.score_survey.question_ids)

        self.assertEqual(without_gate.grade_id.name, "Pass")
        self.assertEqual(with_gate.grade_id.name, "Scoped Pass")

    def test_same_scope_rejects_duplicate_name(self):
        with self.assertRaises(ValidationError):
            self._grade(self.score_survey, "Pass", 20, 30)

    def test_same_scope_rejects_overlapping_range(self):
        with self.assertRaises(ValidationError):
            self._grade(self.score_survey, "Borderline", 4, 7)

    def test_different_scopes_may_overlap(self):
        gate = self._question_worth(self.score_survey, 4)
        yes = gate.suggested_answer_ids.filtered(lambda a: a.value == "Yes")
        # Same name and the very same range as an existing unscoped band
        scoped = self._grade(self.score_survey, "Pass", 6, 10, yes)
        self.assertEqual(len(self.score_survey.grade_ids), 3)
        self.assertEqual(scoped.triggering_answer_ids, yes)

    def test_grades_revalidate_when_written_as_a_set(self):
        self.score_survey.grade_ids.write({"color_class": "info"})
        self.assertEqual(
            set(self.score_survey.grade_ids.mapped("color_class")), {"info"}
        )
