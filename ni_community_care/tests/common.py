#  Copyright (c) 2024 NSTDA

from datetime import timedelta

from odoo import fields
from odoo.fields import Command
from odoo.tests import TransactionCase


class TestServiceEventCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.other_user = cls.env["res.users"].create(
            {
                "name": "Caregiver User",
                "login": "caregiver@test.com",
                "groups_id": [(4, cls.env.ref("base.group_user").id)],
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Test Caregiver", "user_id": cls.other_user.id}
        )
        cls.category = cls.env["ni.service.category"].create(
            {"name": "Test Service Category"}
        )
        cls.patient_type = cls.env["ni.patient.type"].create(
            {"name": "Test Patient Type"}
        )
        cls.service = cls.env["ni.service"].create(
            {
                "name": "Test Service",
                "category_id": cls.category.id,
                "employee_id": cls.employee.id,
                "dayofweek": "0",
            }
        )

    def _make_event(self, start=None, user=None, **vals):
        if start is None:
            start = fields.Datetime.now()
        return self.env["ni.service.event"].create(
            {
                "name": "Test Event",
                "start": start,
                "stop": start + timedelta(hours=1),
                "service_id": self.service.id,
                "service_ids": [Command.set([self.service.id])],
                "patient_type_id": self.patient_type.id,
                "service_category_id": self.category.id,
                **({"user_id": user.id} if user else {}),
                **vals,
            }
        )

    def setUp(self):
        super().setUp()
        self.event = self._make_event()
