#  Copyright (c) 2026 NSTDA

from psycopg2 import IntegrityError

from odoo import fields
from odoo.tests import Form, TransactionCase
from odoo.tools import mute_logger


class TestBirthdateEstimate(TransactionCase):
    def test_partner_older_than_the_module(self):
        """Odoo does not fill a False default: the column of these partners is empty,
        so it cannot be NOT NULL."""
        self.assertFalse(self.env["res.partner"]._fields["birthdate_estimate"].required)
        partner = self.env["res.partner"].create({"name": "Older", "age": 40})
        partner.flush_recordset()
        self.env.cr.execute(
            "UPDATE res_partner SET birthdate_estimate = NULL WHERE id = %s",
            [partner.id],
        )
        partner.invalidate_recordset()
        self.assertFalse(partner.birthdate_estimate)
        partner.name = "Older partner"
        partner.flush_recordset()

    def test_constraint_checks_the_day(self):
        Partner = self.env["res.partner"]
        for birthdate in ("1950-01-01", "1950-05-01", False):
            partner = Partner.create(
                {"name": "P", "birthdate": birthdate, "birthdate_estimate": True}
            )
            self.assertTrue(partner.birthdate_estimate)
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                Partner.create(
                    {
                        "name": "P",
                        "birthdate": "1950-01-02",
                        "birthdate_estimate": True,
                    }
                )

    def test_patient_form(self):
        partner = self.env["res.partner"].create(
            {"name": "Form", "birthdate": "1950-05-17"}
        )
        patient = self.env["ni.patient"].create({"partner_id": partner.id})
        with Form(patient) as form:
            form.birthdate_estimate = True
            self.assertEqual(form.birthdate, fields.Date.to_date("1950-01-01"))
        self.assertTrue(partner.birthdate_estimate)
        self.assertEqual(partner.birthdate, fields.Date.to_date("1950-01-01"))

    def test_patient_form_without_birthdate(self):
        partner = self.env["res.partner"].create({"name": "Form"})
        patient = self.env["ni.patient"].create({"partner_id": partner.id})
        with Form(patient) as form:
            form.birthdate_estimate = True
            today = fields.Date.context_today(patient)
            self.assertEqual(form.birthdate, today.replace(month=1, day=1))
