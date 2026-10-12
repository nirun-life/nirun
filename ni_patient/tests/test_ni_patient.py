#  Copyright (c) 2021-2023 NSTDA

from dateutil.relativedelta import relativedelta
from psycopg2 import IntegrityError

from odoo import fields
from odoo.tests import Form
from odoo.tools import mute_logger

from .common import TestPatientCommon


class TestPatient(TestPatientCommon):
    def test_patient_resource(self):
        madam_glenda = self.env["res.partner"].create(
            {
                "name": "Glenda J Langlois",
                "country_id": self.ref("base.us"),
                "title_id": self.ref("ni_partner_title.res_partner_title_madam"),
            }
        )

        form = Form(self.patient_admin)
        form.partner_id = madam_glenda
        form.save()

        form2 = Form(self.patient_admin)
        form2.partner_id = madam_glenda
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            form2.save()

    def test_age(self):
        form = Form(self.patient_admin)
        form.partner_id = self.env["res.partner"].create({"name": "Eunice"})
        form.save()
        form.birthdate = fields.Date.today() - relativedelta(years=62)

        patient = form.save()

        self.assertEqual(patient.display_age, "62 Years")
        self.assertEqual(patient.deceased, False)

    def test_deceased(self):
        form = Form(self.patient_admin)
        form.partner_id = self.env["res.partner"].create({"name": "Smith"})
        form.save()
        form.birthdate = fields.Date.today() - relativedelta(years=62)
        form.deceased_date = fields.Date.today() - relativedelta(years=2)

        patient = form.save()

        self.assertEqual(patient.display_age, "60 Years")
        self.assertEqual(patient.deceased, True)
