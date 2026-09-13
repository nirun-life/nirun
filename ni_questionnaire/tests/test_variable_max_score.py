#  Copyright (c) 2026 NSTDA
"""MMSE-Thai: a questionnaire whose maximum score moves with one of its own answers.

A respondent who never attended school is not given the Attention/Calculation,
Written Command and Writing items, so the instrument is scored out of 23 instead
of 30. The normal/abnormal cutoff follows the education level: no schooling <=14,
primary <=17, above primary <=22.

Stock Odoo 16 gates a conditional question on exactly one answer, so the three
skipped items hang off a binary "Attended school?" question, while the cutoff
bands hang off a separate three-level "Education level" question. Do not fold
the two back into one question.
"""

from odoo.exceptions import ValidationError
from odoo.tests import common

# (title, max score, only administered to schooled respondents)
MMSE_ITEMS = [
    ("Orientation: Time", 5, False),
    ("Orientation: Place", 5, False),
    ("Registration", 3, False),
    ("Attention/Calculation", 5, True),
    ("Recall", 3, False),
    ("Naming", 2, False),
    ("Repetition", 1, False),
    ("Verbal Command", 3, False),
    ("Written Command", 1, True),
    ("Writing", 1, True),
    ("Visuo-construction", 1, False),
]

CUTOFF = {"none": 14, "primary": 17, "above": 22}


class TestVariableMaxScore(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "MMSE Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})

        cls.normal = cls.env["ni.observation.interpretation"].create(
            {"name": "MMSE Normal", "code": "test-N", "display_class": "success"}
        )
        cls.abnormal = cls.env["ni.observation.interpretation"].create(
            {
                "name": "MMSE Abnormal",
                "code": "test-A",
                "display_class": "danger",
                "is_problem": True,
            }
        )
        cls.obs_type = cls.env["ni.observation.type"].create(
            {
                "name": "MMSE Score",
                "code": "test-mmse",
                "value_type": "int",
                "min": 0,
                "max": 30,
            }
        )

        cls.survey = cls.env["survey.survey"].create(
            {
                "title": "MMSE-Thai 2002",
                "scoring_type": "scoring_without_answers",
                "subject_type": "ni.patient",
                "grading_basis": "score",
                "observation_type_id": cls.obs_type.id,
                "observation_score_type": "raw",
            }
        )

        cls.gate = cls._question("Attended school?", 0, ["Yes", "No"])
        cls.schooled, cls.no_school = cls.gate.suggested_answer_ids
        cls.level = cls._question(
            "Education level",
            1,
            ["Primary", "Above primary"],
            is_conditional=True,
            triggering_question_id=cls.gate.id,
            triggering_answer_id=cls.schooled.id,
        )
        cls.answer_primary, cls.answer_above = cls.level.suggested_answer_ids
        # The answer(s) a respondent of each education level gives to the two
        # questions above; grades key on the last one.
        cls.education = {
            "none": [cls.no_school],
            "primary": [cls.schooled, cls.answer_primary],
            "above": [cls.schooled, cls.answer_above],
        }

        cls.items = {}
        for seq, (title, max_score, schooled_only) in enumerate(MMSE_ITEMS, 2):
            kwargs = {}
            if schooled_only:
                kwargs = {
                    "is_conditional": True,
                    "triggering_question_id": cls.gate.id,
                    "triggering_answer_id": cls.schooled.id,
                }
            cls.items[title] = cls._question(
                title, seq, [str(s) for s in range(max_score + 1)], **kwargs
            )
        cls.q_schooled = cls.items["Attention/Calculation"]

        # Overlapping ranges, kept apart by their triggering answer:
        # no schooling is scored out of 23, the other two out of 30.
        for name, cutoff in CUTOFF.items():
            top = 23 if name == "none" else 30
            trigger = cls.education[name][-1]
            cls._grade("Abnormal", 0, cutoff, trigger, cls.abnormal)
            cls._grade("Normal", cutoff + 1, top, trigger, cls.normal)

    @classmethod
    def _question(cls, title, sequence, answers, **kwargs):
        """Simple choice whose answer score is the answer text ("0".."5"), or 0."""
        vals = {
            "title": title,
            "sequence": sequence,
            "survey_id": cls.survey.id,
            "question_type": "simple_choice",
            "suggested_answer_ids": [
                (
                    0,
                    0,
                    {
                        "value": value,
                        "answer_score": int(value) if value.isdigit() else 0,
                    },
                )
                for value in answers
            ],
        }
        vals.update(kwargs)
        return cls.env["survey.question"].create(vals)

    @classmethod
    def _grade(cls, name, low, high, answer, interpretation):
        return cls.env["survey.grade"].create(
            {
                "survey_id": cls.survey.id,
                "name": name,
                "low": low,
                "high": high,
                "triggering_answer_ids": [(6, 0, answer.ids)],
                "interpretation_id": interpretation.id,
            }
        )

    def _respond(self, education, raw):
        """Answer as a respondent of `education` level scoring `raw` in total.

        Points are poured into the administered items in form order until `raw`
        is reached, so only the total is meaningful.
        """
        picks = []
        remaining = raw
        for title, max_score, schooled_only in MMSE_ITEMS:
            if schooled_only and education == "none":
                continue
            score = min(remaining, max_score)
            remaining -= score
            picks.append(
                self.items[title].suggested_answer_ids.filtered(
                    lambda a, s=score: a.value == str(s)
                )
            )
        assert remaining == 0, "raw score exceeds the administered maximum"

        response = self.env["survey.user_input"].create(
            {
                "survey_id": self.survey.id,
                "patient_id": self.patient.id,
                "subject_model": "ni.patient",
                "subject_id": self.patient.id,
            }
        )
        for answer in self.education[education] + picks:
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

    def test_max_score_follows_the_gate_answer(self):
        """The conditional items leave the denominator when not administered."""
        schooled = self._respond("above", 20)
        unschooled = self._respond("none", 20)

        self.assertIn(self.q_schooled, schooled.predefined_question_ids)
        self.assertNotIn(self.q_schooled, unschooled.predefined_question_ids)

        # Same raw score, different maximum: 20/30 vs 20/23
        self.assertEqual(schooled.scoring_total, 20)
        self.assertEqual(unschooled.scoring_total, 20)
        self.assertEqual(round(schooled.scoring_percentage, 2), 66.67)
        self.assertEqual(round(unschooled.scoring_percentage, 2), 86.96)

    def test_cutoff_follows_the_education_level(self):
        """Each level flips from Abnormal to Normal at its own cutoff (14/17/22)."""
        for education, cutoff in CUTOFF.items():
            with self.subTest(education=education):
                self.assertEqual(
                    self._respond(education, cutoff).grade_id.name, "Abnormal"
                )
                self.assertEqual(
                    self._respond(education, cutoff + 1).grade_id.name, "Normal"
                )

    def test_observation_takes_the_grade_interpretation(self):
        unschooled = self._respond("none", 20)
        observation = self.env["ni.observation"].search(
            [("survey_response_id", "=", unschooled.id)]
        )
        self.assertEqual(len(observation), 1)
        self.assertEqual(observation.value_int, 20)
        self.assertEqual(observation.interpretation_id, self.normal)

    def test_grades_of_different_scope_may_overlap(self):
        """0-14, 0-17 and 0-22 coexist because they answer to different answers."""
        self.assertEqual(len(self.survey.grade_ids), 6)
        with self.assertRaises(ValidationError):
            self._grade("Abnormal", 0, 10, self.no_school, self.abnormal)

    def test_all_grades_revalidate_together(self):
        """A write over the whole set re-runs the constraint on every record."""
        self.survey.grade_ids.write({"color_class": "info"})
        self.assertEqual(set(self.survey.grade_ids.mapped("color_class")), {"info"})

    def test_sheet_or_single_observation_follows_the_administered_items(self):
        """A hidden item stops producing its own observation.

        Two mapped outputs go into a ni.observation.sheet, one goes in on its own.
        """
        item_type = self.env["ni.observation.type"].create(
            {
                "name": "MMSE Attention/Calculation",
                "code": "test-mmse-attention",
                "value_type": "int",
                "min": 0,
                "max": 5,
            }
        )
        self.q_schooled.write(
            {"observation_code_id": item_type.id, "observation_answer_type": "score"}
        )

        schooled = self._respond("primary", 20)
        unschooled = self._respond("none", 20)

        schooled_obs = self.env["ni.observation"].search(
            [("survey_response_id", "=", schooled.id)]
        )
        unschooled_obs = self.env["ni.observation"].search(
            [("survey_response_id", "=", unschooled.id)]
        )
        self.assertEqual(len(schooled_obs), 2)
        self.assertEqual(len(schooled_obs.sheet_id), 1)
        self.assertEqual(len(unschooled_obs), 1)
        self.assertFalse(unschooled_obs.sheet_id)
