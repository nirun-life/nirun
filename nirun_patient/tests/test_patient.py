#  Copyright (c) 2021 Piruin P.

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import Form

from .common import TestPatientCommon


class TestPatient(TestPatientCommon):
    def test_patient_resource(self):
        patient = self.env["ni.patient"].with_user(self.patient_admin)
        form = Form(patient)
        form.partner_id = self.browse_ref("nirun_patient.partner_mrs_glenda")

        patient = form.save()

        self.assertEqual(patient.name, "Glenda J Langlois")
        self.assertEqual(patient.company_id, self.env.company)

    def test_age(self):
        patient = self.env["ni.patient"].with_user(self.patient_admin)
        form = Form(patient)
        form.firstname = "Eunice"
        form.birthdate = fields.date.today() - relativedelta(years=62)

        patient = form.save()

        self.assertEqual(patient.age, "62 Years")
        self.assertEqual(patient.deceased, False)

    def test_deceased(self):
        patient = self.env["ni.patient"].with_user(self.patient_admin)
        form = Form(patient)
        form.firstname = "Eunice"
        form.birthdate = fields.date.today() - relativedelta(years=62)
        form.deceased_date = fields.date.today() - relativedelta(years=2)

        patient = form.save()

        self.assertEqual(patient.age, "60 Years")
        self.assertEqual(patient.deceased, True)

    def test_inverse_age(self):
        patient = self.env["ni.patient"].with_user(self.patient_admin)
        form = Form(patient)
        form.age_years = 62

        patient = form.save()

        self.assertEqual(
            patient.birthdate, fields.date.today() - relativedelta(years=62)
        )
