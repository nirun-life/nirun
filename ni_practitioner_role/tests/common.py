#  Copyright (c) 2026 NSTDA

from odoo.tests import TransactionCase


class TestPractitionerRoleCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.other_company = cls.env["res.company"].create({"name": "Second Clinic"})
        cls.category = cls.env["hr.employee.category"].create({"name": "Test nurse"})
        cls.role = cls.env["res.users.role"].create(
            {"name": "Test role", "employee_category_ids": [(4, cls.category.id)]}
        )

    @classmethod
    def _create_user(cls, login, **vals):
        return cls.env["res.users"].create({"name": login, "login": login, **vals})
