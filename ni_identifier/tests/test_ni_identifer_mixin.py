#  Copyright (c) 2023 NSTDA

from odoo_test_helper import FakeModelLoader

from odoo.release import version_info

if version_info[0] < 15:
    from odoo.tests import SavepointCase as TransactionCase
else:
    # Odoo 15 and later: TransactionCase rolls back between tests
    from odoo.tests import TransactionCase


class TestMixin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestMixin, cls).setUpClass()

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        from .test_models import ResPartner

        cls.loader.update_registry((ResPartner,))

        cls.env["ir.sequence"].create(
            {
                "name": "Partner Identifier",
                "code": "res.partner",
                "prefix": "PRN-",
                "padding": 5,
                "number_next": 1,
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super(TestMixin, cls).tearDownClass()

    def test_create(self):
        partner = self.env["res.partner"].create({"name": "BAR"})
        self.assertEqual(partner.name, "BAR")
        self.assertEqual(partner.identifier, "PRN-00001")
