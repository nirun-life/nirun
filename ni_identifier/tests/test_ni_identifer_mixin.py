#  Copyright (c) 2023 NSTDA

from odoo_test_helper import FakeModelLoader

from odoo.tests import TransactionCase


class TestMixin(TransactionCase):
    # Odoo 18 checks the registry after each test, so the fake model is loaded
    # and restored per test (odoo-test-helper "Right Way (v18)").
    def setUp(self):
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()

        from .test_models import ResPartner

        self.loader.update_registry((ResPartner,))

        self.env["ir.sequence"].create(
            {
                "name": "Partner Identifier",
                "code": "res.partner",
                "prefix": "PRN-",
                "padding": 5,
                "number_next": 1,
            }
        )

    def tearDown(self):
        self.loader.restore_registry()
        super().tearDown()

    def test_create(self):
        partner = self.env["res.partner"].create({"name": "BAR"})
        self.assertEqual(partner.name, "BAR")
        self.assertEqual(partner.identifier, "PRN-00001")
