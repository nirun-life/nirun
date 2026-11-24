#  Copyright (c) 2026 NSTDA

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form

from .common import TestPractitionerCommon


class TestHrResumeLine(TestPractitionerCommon):
    def _name(self, line, **context):
        line.invalidate_recordset(["display_name"])
        return line.with_context(**context).display_name

    def test_display_name(self):
        self.assertEqual(self._name(self.license), "Nursing license")
        self.assertEqual(
            self._name(self.license, show_identifier=True), "Nursing license • N-0001"
        )

    def test_display_name_without_identifier(self):
        line = self._create_line(self.performer, "Some course")
        self.assertEqual(self._name(line, show_identifier=True), "Some course")

    def test_display_name_with_period(self):
        line = self._create_line(
            self.performer, "Old license", "N-0000", date_end="2021-02-28"
        )
        self.assertEqual(
            self._name(line, show_period=True), "Old license 2020-01-31 - 2021-02-28"
        )
        self.assertEqual(
            self._name(self.license, show_identifier=True, show_period=True),
            "Nursing license • N-0001 2020-01-31 - Current",
        )

    def test_code_fills_the_line(self):
        issuer = self.env["res.partner"].create(
            {"name": "Test council", "is_company": True}
        )
        code = self.env["hr.resume.line.code"].create(
            {
                "name": "Test license code",
                "issuer_id": issuer.id,
                "type_id": self.line_type.id,
                "system_id": self.env.ref("ni_coding.system_internal").id,
            }
        )
        line = self.env["hr.resume.line"].new({"employee_id": self.performer.id})
        line.code_id = code
        line._onchange_code_id()
        self.assertEqual(line.name, "Test license code")
        self.assertEqual(line.issuer_id, issuer)
        self.assertEqual(line.line_type_id, self.line_type)

    def test_dates(self):
        with self.assertRaises(ValidationError):
            self._create_line(
                self.performer,
                "Future",
                date_start=fields.Date.add(fields.Date.today(), days=2),
            )

    def test_form_requires_the_credential_of_the_code(self):
        code = self.env["hr.resume.line.code"].create(
            {
                "name": "Licensed code",
                "require_identifier": True,
                "type_id": self.line_type.id,
                "system_id": self.env.ref("ni_coding.system_internal").id,
            }
        )
        form = Form(
            self.env["hr.resume.line"].with_context(
                default_employee_id=self.performer.id
            ),
            view="hr_skills.resume_line_view_form",
        )
        form.date_start = "2020-01-31"
        form.code_id = code
        self.assertEqual(form.name, "Licensed code")
        with self.assertRaises(AssertionError):
            form.save()
        form.identifier = "L-1"
        self.assertEqual(form.save().identifier, "L-1")
