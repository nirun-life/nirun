#  Copyright (c) 2026 NSTDA

from datetime import datetime

from freezegun import freeze_time

from odoo.exceptions import ValidationError
from odoo.tests import common

NOW = datetime(2026, 9, 20, 10, 0, 0)
PAST = datetime(2026, 9, 17, 10, 0, 0)
FUTURE = datetime(2026, 9, 21, 10, 0, 0)


@freeze_time(NOW)
class TestRetrospectiveWizard(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.survey = cls.env["survey.survey"].create(
            {"title": "Retrospective", "subject_type": "res.partner"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Subject"})
        cls.Wizard = cls.env["survey.subject.wizard"]

    def _wizard(self, **vals):
        return self.Wizard.create(
            {
                "survey_id": self.survey.id,
                "subject_res_partner": self.partner.id,
                **vals,
            }
        )

    def _last_answer(self):
        answer = self.env["survey.user_input"].search(
            [("survey_id", "=", self.survey.id)], order="id desc", limit=1
        )
        answer.invalidate_recordset()  # create_date is rewritten with raw SQL
        return answer

    def test_retrospective_backdates_answer_and_marks_started(self):
        wizard = self._wizard(retrospective=True, survey_date=PAST)
        wizard.action_survey()

        answer = self._last_answer()
        self.assertTrue(answer.retrospective)
        self.assertEqual(answer.create_date, PAST)
        self.assertTrue(wizard.started)

    def test_non_retrospective_ignores_survey_date(self):
        wizard = self._wizard(retrospective=False, survey_date=PAST)
        wizard.action_survey()

        answer = self._last_answer()
        self.assertFalse(answer.retrospective)
        self.assertNotEqual(answer.create_date, PAST)
        self.assertTrue(wizard.started)

    def test_survey_date_constraints(self):
        with self.assertRaises(ValidationError):
            self._wizard(retrospective=True)
        with self.assertRaises(ValidationError):
            self._wizard(retrospective=True, survey_date=FUTURE)
