#  Copyright (c) 2023 NSTDA

from odoo.orm.model_classes import add_to_registry
from odoo.tests import TransactionCase


class TestMixin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        from .test_models import NiIdentifierTest

        add_to_registry(cls.registry, NiIdentifierTest)
        cls.registry._setup_models__(cls.env.cr, ["ni.identifier.test"])
        cls.registry.init_models(
            cls.env.cr, ["ni.identifier.test"], {"models_to_check": True}
        )
        cls.addClassCleanup(cls.registry.__delitem__, "ni.identifier.test")

        cls.env["ir.sequence"].create(
            {
                "name": "Test Identifier",
                "code": "ni.identifier.test",
                "prefix": "TST-",
                "padding": 5,
                "number_next": 1,
            }
        )

    def test_create(self):
        record = self.env["ni.identifier.test"].create({"name": "BAR"})
        self.assertEqual(record.name, "BAR")
        self.assertEqual(record.identifier, "TST-00001")

    def test_create_without_sequence(self):
        self.env["ir.sequence"].search([("code", "=", "ni.identifier.test")]).unlink()
        logger = "odoo.addons.ni_identifier.models.ni_identifer_mixin"
        with self.assertLogs(logger, level="WARNING"):
            record = self.env["ni.identifier.test"].create({"name": "BAR"})
        self.assertEqual(record.identifier, "New")
