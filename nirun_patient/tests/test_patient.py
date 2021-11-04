#  Copyright (c) 2021 Piruin P.

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import Form

from .common import TestPatientCommon


class TestPatient(TestPatientCommon):
    def test_patient_resource(self):
        patients = self.env["ni.patient"].with_user(self.patient_admin)
        form = Form(patients)

        madam_glenda = self.env["res.partner"].create(
            {
                "name": "Glenda J Langlois",
                "country_id": self.ref("base.us"),
                "title": self.ref("base.res_partner_title_madam"),
            }
        )
        form.partner_id = madam_glenda
        form.save()

        form2 = Form(patients)
        form2.partner_id = madam_glenda
        try:
            form2.save()
        except Exception:
            self.assertEqual(True, True, "Raised UniqueViolation")
        else:
            self.assertEqual(True, False, "Not raise UniqueViolation")

    def test_age(self):
        patient = self.env["ni.patient"].with_user(self.patient_admin)
        form = Form(patient)
        form.partner_id = self.env["res.partner"].create({"name": "Eunice"})
        form.birthdate = fields.date.today() - relativedelta(years=62)

        patient = form.save()

        self.assertEqual(patient.age, "62 Years")
        self.assertEqual(patient.deceased, False)

    def test_deceased(self):
        patient = self.env["ni.patient"].with_user(self.patient_admin)
        form = Form(patient)
        form.partner_id = self.env["res.partner"].create({"name": "Eunice"})
        form.birthdate = fields.date.today() - relativedelta(years=62)
        form.deceased_date = fields.date.today() - relativedelta(years=2)

        patient = form.save()

        self.assertEqual(patient.age, "60 Years")
        self.assertEqual(patient.deceased, True)

    def test_inverse_age(self):
        patient = self.env["ni.patient"].with_user(self.patient_admin)
        form = Form(patient)
        form.partner_id = self.env["res.partner"].create({"name": "Eunice"})
        form.age_years = 62

        patient = form.save()

        self.assertEqual(
            patient.birthdate, fields.date.today() - relativedelta(years=62)
        )
