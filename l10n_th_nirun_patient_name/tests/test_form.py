#  Copyright (c) 2021 Piruin P.

from odoo.tests.common import Form, TransactionCase


class TestL10nThPatientForm(TransactionCase):
    def setUp(self):
        super().setUp()
        self.create_title()
        self.form = Form(self.env["ni.patient"])

    def create_title(self):
        self.title = self.env["res.partner.title"].create({"name": "Sensei"})

    def test_patient_name_onchange(self):
        """Test that you change title"""
        self.form.lastname = "Panichphol"
        self.assertEqual(self.form.name, "Panichphol")

        self.form.firstname = "Piruin"
        self.assertEqual(self.form.name, "Piruin Panichphol")

        self.form.title = self.title
        self.assertEqual(self.form.name, "Sensei Piruin Panichphol")

    def test_patient_name_on_save(self):
        """Test that you change title"""
        self.form.title = self.title
        self.form.lastname = "Panichphol"
        self.form.firstname = "Piruin"
        patient = self.form.save()

        self.assertEqual(patient.name, "Sensei Piruin Panichphol")
