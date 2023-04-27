#  Copyright (c) 2021-2023 NSTDA

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import Form

from .common import TestPatientCommon


class TestPatient(TestPatientCommon):
    def test_patient_resource(self):
        madam_glenda = self.env["res.partner"].create(
            {
                "name": "Glenda J Langlois",
                "country_id": self.ref("base.us"),
                "title": self.ref("base.res_partner_title_madam"),
            }
        )

        form = Form(self.patient_admin)
        form.partner_id = madam_glenda
        form.save()

        form2 = Form(self.patient_admin)
        form2.partner_id = madam_glenda
        try:
            form2.save()
        except Exception:
            self.assertEqual(True, True, "Raised UniqueViolation")
        else:
            self.assertEqual(True, False, "Not raise UniqueViolation")

    def test_age(self):
        form = Form(self.patient_admin)
        form.partner_id = self.env["res.partner"].create({"name": "Eunice"})
        form.save()
        form.birthdate = fields.date.today() - relativedelta(years=62)

        patient = form.save()

        self.assertEqual(patient.display_age, "62 Years")
        self.assertEqual(patient.deceased, False)

    def test_deceased(self):
        form = Form(self.patient_admin)
        form.partner_id = self.env["res.partner"].create({"name": "Smith"})
        form.save()
        form.birthdate = fields.date.today() - relativedelta(years=62)
        form.deceased_date = fields.date.today() - relativedelta(years=2)

        patient = form.save()

        self.assertEqual(patient.display_age, "60 Years")
        self.assertEqual(patient.deceased, True)
