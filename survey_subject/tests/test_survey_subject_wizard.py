#  Copyright (c) 2026 NSTDA

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestSurveySubjectWizard(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.survey = cls.env["survey.survey"].create(
            {"title": "Subject Wizard", "subject_type": "res.partner"}
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

    def test_prepare_answer_moves_to_survey_step(self):
        wizard = self._wizard()
        self.assertEqual(wizard.state, "choose")
        action = wizard.prepare_answer()
        self.assertEqual(wizard.state, "survey")
        self.assertEqual(action["res_id"], wizard.id)

    def test_action_survey_creates_answer_and_marks_started(self):
        wizard = self._wizard()
        self.assertFalse(wizard.started)
        action = wizard.action_survey()

        answer = self.env["survey.user_input"].search(
            [("survey_id", "=", self.survey.id)], order="id desc", limit=1
        )
        self.assertEqual(answer.subject_model, "res.partner")
        self.assertEqual(answer.subject_id, self.partner.id)
        self.assertEqual(answer.partner_id, self.env.user.partner_id)
        self.assertTrue(wizard.started)
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertIn(
            "/survey/%s/%s" % (self.survey.access_token, answer.access_token),
            action["url"],
        )

    def test_missing_subject_is_rejected(self):
        wizard = self._wizard(subject_res_partner=False)
        with self.assertRaises(ValidationError):
            wizard.action_survey()
