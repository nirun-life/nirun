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

    def test_display_name(self):
        self.assertEqual(self.company.display_name, "Nirun Test Hospital (NTH-0001)")
        company = self.company.with_context(no_identifier=True)
        self.assertEqual(company.display_name, "Nirun Test Hospital")
        self.company.identifier = False
        self.assertEqual(self.company.display_name, "Nirun Test Hospital")

    def test_name_search(self):
        Company = self.env["res.company"]
        other = Company.create({"name": "Nirun Clinic", "identifier": "NTH-0002"})

        def found(name, **kwargs):
            return {rec_id for rec_id, _name in Company.name_search(name, **kwargs)}

        self.assertEqual(found("NTH-0001"), {self.company.id})
        self.assertEqual(found("Test Hospital"), {self.company.id})
        self.assertEqual(found("Hospital Nirun"), {self.company.id})
        self.assertEqual(
            found("Nirun") & {self.company.id, other.id}, {self.company.id, other.id}
        )
        self.assertFalse(found("NTH-0001 Clinic"))
        self.assertEqual(
            found("Nirun", domain=[("id", "!=", other.id)])
            & {self.company.id, other.id},
            {self.company.id},
        )
