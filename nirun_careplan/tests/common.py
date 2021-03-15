#  Copyright (c) 2021 Piruin P.

from odoo.tests import common

from odoo.addons.test_mail.tests.common import mail_new_test_user


class TestCareplanCommon(common.TransactionCase):
    def setUp(self):
        super(TestCareplanCommon, self).setUp()

        self.care_manager = mail_new_test_user(
            self.env,
            login="care-manager",
            groups="base.group_user,nirun_careplan.careplan_group_manager",
            name="Chole Manager",
            email="p.admin@example.com",
        )
        self.caregiver = mail_new_test_user(
            self.env,
            login="caregiver",
            groups="base.group_user,nirun_careplan.careplan_group_user",
            name="Chole Manager",
            email="p.admin@example.com",
        )
