#  Copyright (c) 2021 Piruin P.

from odoo.tests import common

from odoo.addons.test_mail.tests.common import mail_new_test_user


class TestPatientCommon(common.TransactionCase):
    def setUp(self):
        super(TestPatientCommon, self).setUp()

        self.patient_admin = mail_new_test_user(
            self.env,
            login="patient",
            groups="base.group_user,nirun_patient.group_user",
            name="Patient Administrator",
            email="p.admin@example.com",
        )
