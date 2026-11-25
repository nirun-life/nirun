#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestCompletionPage(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Subject P."})
        cls.user = common.new_test_user(
            cls.env, login="subject.user", name="Subject U."
        )

    def _page(self, subject, scoring_type="scoring_with_answers"):
        survey = self.env["survey.survey"].create(
            {
                "title": "Completion",
                "scoring_type": scoring_type,
                "scoring_success_min": 0,
                "subject_type": subject._name,
            }
        )
        answer = self.env["survey.user_input"].create(
            {
                "survey_id": survey.id,
                "subject_model": subject._name,
                "subject_id": subject.id,
            }
        )
        page = self.env["ir.qweb"]._render(
            "survey.survey_fill_form_done",
            {"survey": survey, "answer": answer, "graph_data": False},
        )
        return " ".join(str(page).split())

    def test_partner_subject(self):
        page = self._page(self.partner)
        self.assertIn("You scored", page)
        self.assertNotIn("Thank you!", page)
        self.assertNotIn("Subject P. scored", page)
        self.assertNotIn("Acknowledge Results", page)

    def test_other_subject(self):
        page = self._page(self.user)
        self.assertIn("Thank you!", page)
        self.assertNotIn("You scored", page)
        self.assertIn("Subject U. scored", page)
        self.assertIn("Acknowledge Results", page)

    def test_no_scoring(self):
        for subject in (self.partner, self.user):
            with self.subTest(subject=subject._name):
                page = self._page(subject, scoring_type="no_scoring")
                self.assertIn("Thank you!", page)
                self.assertNotIn("scored", page)
