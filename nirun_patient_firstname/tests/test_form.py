#  Copyright (c) 2021 Piruin P.
from odoo.tests.common import Form, TransactionCase


class PatientOnchangeCase(TransactionCase):
    def test_form_with_firstname_lastname(self):
        """In a new users form, a patient set only the firstname."""
        firstname = "Piruin"
        lastname = "Panichphol"
        patient_form = Form(
            self.env["ni.patient"],
            view="nirun_patient_firstname.patient_view_form_inherit",
        )

        # Changes firstname, which triggers onchanges
        patient_form.firstname = firstname
        patient_form.lastname = lastname
        patient = patient_form.save()

        self.assertEqual(patient.lastname, lastname)
        self.assertEqual(patient.firstname, firstname)
        self.assertEqual(patient.name, "Piruin Panichphol")

    def test_form_with_firstname_only(self):
        """In a new users form, a patient set only the firstname."""
        firstname = "Piruin"
        patient_form = Form(
            self.env["ni.patient"],
            view="nirun_patient_firstname.patient_view_form_inherit",
        )

        # Changes firstname, which triggers onchanges
        patient_form.firstname = firstname
        patient = patient_form.save()

        self.assertEqual(patient.firstname, firstname)
        self.assertEqual(patient.name, firstname)
