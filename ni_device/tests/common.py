from odoo import fields
from odoo.tests import common


class TestDeviceCommon(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.manufacturer = cls.env["res.partner"].create(
            {"name": "Acme Medical", "is_company": True}
        )
        cls.definition = cls.env["ni.device.definition"].create(
            {
                "name": "Portable BP Monitor",
                "manufacturer_id": cls.manufacturer.id,
                "model_number": "BP-100",
            }
        )
        cls.device = cls.env["ni.device"].create(
            {
                "name": "BP Monitor #1",
                "definition_id": cls.definition.id,
                "serial_number": "SN-001",
                "received_date": fields.Date.today(),
            }
        )

        cls.employee = cls.env["hr.employee"].create({"name": "Test Holder"})
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
