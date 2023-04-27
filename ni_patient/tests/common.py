#  Copyright (c) 2021-2023 NSTDA

from odoo.tests import common


class TestPatientCommon(common.TransactionCase):
    def setUp(self):
        super(TestPatientCommon, self).setUp()

        patient_admin = self.env["res.users"].create(
            {
                "login": "Patient.User",
                "groups_id": [
                    (4, self.ref("base.group_user"), 0),
                    (4, self.ref("ni_patient.group_admin"), 0),
                ],
                "name": "Patient Admin",
                "email": "p.admin@example.com",
                "password": "admin",
            }
        )
        self.patient_admin = self.env["ni.patient"].with_user(patient_admin)
