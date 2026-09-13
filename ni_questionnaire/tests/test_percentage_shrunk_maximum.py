#  Copyright (c) 2026 NSTDA
"""Regression guard for creating observations before _mark_done() trims.

_mark_done() drops the conditional questions that were never shown from
predefined_question_ids, which shrinks the maximum behind scoring_percentage.
Under the points basis the pre-trim and post-trim numbers are identical, so only
a percentage-scored survey can catch an observation created too early.
"""

from odoo.tests import common


class TestPercentageOfShrunkMaximum(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "Percent Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})

        percent_type = cls.env["ni.observation.type"].create(
            {
                "name": "Screening Percent",
                "code": "test-screen-pct",
                "value_type": "float",
                "min": 0,
                "max": 100,
            }
        )
        cls.survey = cls.env["survey.survey"].create(
            {
                "title": "Percent Screening",
                "scoring_type": "scoring_without_answers",
                "subject_type": "ni.patient",
                "grading_basis": "percentage",
                "observation_type_id": percent_type.id,
                "observation_score_type": "percentage",
            }
        )

        # Gate + one item for everyone (4 pts) + one item behind the gate (4 pts)
        cls.gate = cls._question("Show the extra item?", [("Yes", 0), ("No", 0)])
        cls.answer_yes, cls.answer_no = cls.gate.suggested_answer_ids
        cls.common = cls._question("Common item", [("0", 0), ("4", 4)])
        cls.extra = cls._question(
            "Extra item",
            [("0", 0), ("4", 4)],
            is_conditional=True,
            triggering_question_id=cls.gate.id,
            triggering_answer_id=cls.answer_yes.id,
        )

    @classmethod
    def _question(cls, title, answers, **kwargs):
        vals = {
            "title": title,
            "survey_id": cls.survey.id,
            "question_type": "simple_choice",
            "suggested_answer_ids": [
                (0, 0, {"value": value, "answer_score": score})
                for value, score in answers
            ],
        }
        vals.update(kwargs)
        return cls.env["survey.question"].create(vals)

    def _respond(self, answers):
        response = self.env["survey.user_input"].create(
            {
                "survey_id": self.survey.id,
                "patient_id": self.patient.id,
                "subject_model": "ni.patient",
                "subject_id": self.patient.id,
            }
        )
        for answer in answers:
            self.env["survey.user_input.line"].create(
                {
                    "user_input_id": response.id,
                    "survey_id": self.survey.id,
                    "question_id": answer.question_id.id,
                    "skipped": False,
                    "answer_type": "suggestion",
                    "suggested_answer_id": answer.id,
                }
            )
        response._mark_done()
        return response

    def test_percentage_observation_uses_the_shrunk_maximum(self):
        four = self.common.suggested_answer_ids[1]
        response = self._respond([self.answer_no, four])
        observation = self.env["ni.observation"].search(
            [("survey_response_id", "=", response.id)]
        )
        # 4 of 4, not 4 of 8
        self.assertEqual(response.scoring_percentage, 100.0)
        self.assertEqual(observation.value_float, 100.0)
