#  Copyright (c) 2026 NSTDA
"""Start and print the encounter's questionnaire on the encounter's own response."""

from odoo.tests import common, new_test_user


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

    def test_start_as_clinician(self):
        """A clinician who did not create the survey can start it from the
        encounter (core only lets a survey officer create answers on their own
        surveys)."""
        clinician = new_test_user(
            self.env, login="encounter_survey_clinician", groups="ni_patient.group_user"
        )
        self.assertNotEqual(self.survey.create_uid, clinician)
        encounter = self.encounter.with_user(clinician)
        action = encounter.action_start_survey()
        response = encounter.response_id
        self.assertTrue(response)
        self.assertEqual(response.partner_id, clinician.partner_id)
        self.assertIn(f"answer_token={response.access_token}", action["url"])

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

    def test_latest_response_ties_on_create_date(self):
        """Two responses created in one transaction share their create_date: the
        latest-response view and the encounter's compute both pick the last one."""
        responses = self.env["survey.user_input"]
        for _i in range(2):
            responses |= self.survey._create_answer(
                user=self.env.user,
                subject_model="ni.encounter",
                subject_id=self.encounter.id,
                patient_id=self.encounter.patient_id.id,
                encounter_id=self.encounter.id,
            )
        responses._mark_done()
        self.env.flush_all()
        self.env.invalidate_all()
        self.assertEqual(len(set(responses.mapped("create_date"))), 1)
        last = max(responses.ids)
        self.assertEqual(self.encounter.response_latest_id.id, last)
        self.assertEqual(self.encounter.response_latest_ids.ids, [last])
