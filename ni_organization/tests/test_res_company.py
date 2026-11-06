#  Copyright (c) 2026 NSTDA
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestResCompany(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.org_type = cls.env.ref("ni_organization.type_prov")
        cls.company = cls.env["res.company"].create(
            {"name": "Nirun Test Hospital", "identifier": "NTH-0001"}
        )

    def test_type_id_not_null(self):
        self.env.cr.execute(
            """
            SELECT is_nullable FROM information_schema.columns
            WHERE table_name = 'res_company' AND column_name = 'type_id'
            """
        )
        self.assertEqual(self.env.cr.fetchone()[0], "NO")
        self.assertFalse(
            self.env["res.company"]
            .with_context(active_test=False)
            .search_count([("type_id", "=", False)])
        )
        self.assertEqual(self.company.type_id, self.org_type)

    def test_display_capacity(self):
        self.assertFalse(self.company.display_capacity)
        self.company.write({"capacity": 30, "capacity_unit": "bed"})
        self.assertEqual(self.company.display_capacity, "30 Beds")
        self.company.capacity_unit = "pat"
        self.assertEqual(self.company.display_capacity, "30 Patients per Day")
