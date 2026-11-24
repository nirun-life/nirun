#  Copyright (c) 2026 NSTDA

from odoo.tests import TransactionCase


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

    def test_report(self):
        document = self.env["ni.document.ref"].create(
            {
                "patient_id": self.patient.id,
                "type_id": self.doc_type.id,
                "data": "<p>Report body</p>",
            }
        )
        html, _type = self.env["ir.actions.report"]._render_qweb_html(
            "ni_document_ref.action_report_document", document.ids
        )
        self.assertIn("Report body", html.decode())
