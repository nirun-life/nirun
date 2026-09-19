#  Copyright (c) 2026 NSTDA
"""The survey completion page, with every extension of it applied.

`survey_grading` and `survey_subject` both extend `survey.survey_fill_form_done`
inside the same column, and `survey_subject` addresses its target positionally
(`t[1]/div`). Neither module can see the other, so the combination is only ever
exercised here, where both are installed. The badge and verdict rules themselves
belong to `survey_grading/tests/test_survey_grade.py`.
"""

from odoo.tests import common


class TestCompletionPage(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.survey = self.env["survey.survey"].create(
            {
                "title": "Points, no passing mark",
                "scoring_type": "scoring_with_answers",
                # A percentage passing mark is meaningless under the points basis,
                # so these questionnaires leave it at 0.
                "scoring_success_min": 0,
                "grading_basis": "score",
                "subject_type": "res.partner",
            }
        )
        self.env["survey.question"].create(
            {
                "title": "Q",
                "survey_id": self.survey.id,
                "question_type": "simple_choice",
                "suggested_answer_ids": [
                    (0, 0, {"value": "Yes", "answer_score": 6}),
                    (0, 0, {"value": "No", "answer_score": 0}),
                ],
            }
        )
        self.env["survey.grade"].create(
            {"survey_id": self.survey.id, "name": "Unmistakable", "low": 0, "high": 10}
        )

    def _respond(self, value="Yes"):
        response = self.env["survey.user_input"].create({"survey_id": self.survey.id})
        question = self.survey.question_ids[0]
        answer = question.suggested_answer_ids.filtered(lambda a: a.value == value)
        self.env["survey.user_input.line"].create(
            {
                "user_input_id": response.id,
                "survey_id": self.survey.id,
                "question_id": question.id,
                "skipped": False,
                "answer_type": "suggestion",
                "suggested_answer_id": answer.id,
            }
        )
        response._mark_done()
        return response

    def test_every_extension_still_locates_its_target(self):
        """Raises "cannot be located in parent view" if one xpath has been shifted."""
        self.env.ref("survey.survey_fill_form_done")._get_combined_arch()

    def _page(self, response):
        return str(
            self.env["ir.qweb"]._render(
                "survey.survey_fill_form_done",
                {
                    "survey": self.survey,
                    "answer": response,
                    "graph_data": False,
                    "is_partner_subject": True,
                },
            )
        )

    def test_grade_badge_survives_a_survey_with_no_passing_mark(self):
        response = self._respond()
        self.assertEqual(response.grade_id.name, "Unmistakable")
        self.assertIn("Unmistakable", self._page(response))
