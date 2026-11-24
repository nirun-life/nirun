#  Copyright (c) 2026 NSTDA

from odoo.tests import Form, TransactionCase


class TestDocumentRef(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["ni.patient"].create(
            {"partner_id": cls.env["res.partner"].create({"name": "Document P."}).id}
        )
        cls.doc_type = cls.env["ni.document.ref.type"].create(
            {"name": "Test Type", "code": "TTY"}
        )

    def _create_document(self, **kwargs):
        return self.env["ni.document.ref"].create(
            {"patient_id": self.patient.id, "type_id": self.doc_type.id, **kwargs}
        )

    def test_report(self):
        document = self._create_document(data="<p>Report body</p>")
        html, _type = self.env["ir.actions.report"]._render_qweb_html(
            "ni_document_ref.action_report_document", document.ids
        )
        self.assertIn("Report body", html.decode())

    def test_default_type_of_job(self):
        job = self.env["hr.job"].create(
            {"name": "Test job", "document_ref_type_id": self.doc_type.id}
        )
        employee = self.env["hr.employee"].create(
            {"name": "Author", "job_id": job.id, "user_id": self.env.user.id}
        )
        with Form(job) as form:
            self.assertEqual(form.document_ref_type_id, self.doc_type)
        form = Form(
            self.env["ni.document.ref"].with_context(default_patient_id=self.patient.id)
        )
        self.assertEqual(form.type_id, self.doc_type)
        self.assertEqual(form.author_id, employee)

    def test_author(self):
        author, user_employee = self.env["hr.employee"].create(
            [{"name": "Author"}, {"name": "Me", "user_id": self.env.user.id}]
        )
        document = self._create_document(author_id=author.id)
        self.assertEqual(document.author_ids, author | user_employee)

    def test_template_of_type(self):
        self.doc_type.data_template = "<p>Template</p>"
        form = Form(
            self.env["ni.document.ref"].with_context(default_patient_id=self.patient.id)
        )
        form.type_id = self.doc_type
        self.assertIn("Template", form.data)

    def test_locked_when_completed(self):
        document = self._create_document(data="<p>Body</p>")
        self.assertEqual(document.state, "in-progress")
        with Form(document) as form:
            form.data = "<p>New body</p>"
        document.action_complete()
        with Form(document) as form, self.assertRaises(AssertionError):
            form.data = "<p>Locked</p>"

    def test_count(self):
        encounter = self.env["ni.encounter"].create(
            {
                "patient_id": self.patient.id,
                "class_id": self.env.ref("ni_patient.class_AMB").id,
            }
        )
        document = self._create_document(encounter_id=encounter.id)
        self.assertEqual(encounter.document_count, 1)
        self.assertTrue(document.no_data)
        self.assertEqual(document.attachment_count, 0)
        self.assertTrue(encounter.action_document_ref())
