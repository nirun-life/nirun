#  Copyright (c) 2026 NSTDA
"""Start and print the encounter's questionnaire on the encounter's own response."""

from odoo.tests import common


class TestEncounterSurvey(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.survey = cls.env["survey.survey"].create(
            {"title": "Encounter Questionnaire", "subject_type": "ni.encounter"}
        )
        encounter_class = cls.env["ni.encounter.class"].create(
            {"name": "Questionnaire Class", "survey_id": cls.survey.id}
        )
        partner = cls.env["res.partner"].create({"name": "Encounter Survey Patient"})
        patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.encounter = cls.env["ni.encounter"].create(
            {"patient_id": patient.id, "class_id": encounter_class.id}
        )

    def test_start_creates_and_reuses_the_response(self):
        action = self.encounter.action_start_survey()
        response = self.encounter.response_id
        self.assertTrue(response)
        self.assertEqual(response.survey_id, self.survey)
        self.assertEqual(response.encounter_id, self.encounter)
        self.assertEqual(response.patient_id, self.encounter.patient_id)
        # Filled in by the current user, so core's partner check lets them in.
        self.assertEqual(response.partner_id, self.env.user.partner_id)
        self.assertIn(f"answer_token={response.access_token}", action["url"])
        self.assertEqual(action["target"], "new")

        again = self.encounter.action_start_survey()
        self.assertEqual(self.encounter.response_id, response)
        self.assertIn(f"answer_token={response.access_token}", again["url"])

    def test_print_uses_the_response(self):
        blank = self.encounter.action_print_survey()
        self.assertNotIn("answer_token=False", blank["url"])
        self.encounter.action_start_survey()
        token = self.encounter.response_id.access_token
        action = self.encounter.action_print_survey()
        self.assertIn(f"answer_token={token}", action["url"])
        self.assertEqual(action["target"], "new")

    def test_latest_response_after_done(self):
        """The encounter's latest response (and its print button) follows completion."""
        self.encounter.action_start_survey()
        response = self.encounter.response_id
        self.assertFalse(self.encounter.response_latest_id)
        response._mark_done()
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertEqual(self.encounter.response_latest_id.id, response.id)
