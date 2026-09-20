#  Copyright (c) 2026 NSTDA

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


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
        return self.env["survey.user_input"].search(
            [("survey_id", "=", self.survey.id)], order="id desc", limit=1
        )

    def test_retrospective_backdates_answer_and_marks_started(self):
        survey_date = fields.Datetime.now().replace(microsecond=0) - timedelta(days=3)
        wizard = self._wizard(retrospective=True, survey_date=survey_date)
        wizard.action_survey()

        answer = self._last_answer()
        self.assertTrue(answer.retrospective)
        self.assertEqual(answer.create_date, survey_date)
        self.assertTrue(wizard.started)

    def test_non_retrospective_keeps_create_date(self):
        wizard = self._wizard()
        wizard.action_survey()

        answer = self._last_answer()
        self.assertFalse(answer.retrospective)
        self.assertAlmostEqual(
            answer.create_date, fields.Datetime.now(), delta=timedelta(minutes=1)
        )
        self.assertTrue(wizard.started)

    def test_survey_date_constraints(self):
        with self.assertRaises(ValidationError):
            self._wizard(retrospective=True)
        with self.assertRaises(ValidationError):
            self._wizard(
                retrospective=True,
                survey_date=fields.Datetime.now() + timedelta(days=1),
            )
