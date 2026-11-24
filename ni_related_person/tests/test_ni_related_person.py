#  Copyright (c) 2026 NSTDA

from odoo.tests import TransactionCase


class TestRelatedPerson(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["ni.patient"].create(
            {
                "partner_id": cls.env["res.partner"]
                .create(
                    {
                        "name": "Related P.",
                        "street": "99 Moo 1",
                        "city": "Khlong Luang",
                        "zip": "12120",
                        "country_id": cls.env.ref("base.th").id,
                    }
                )
                .id
            }
        )

    def test_copy_patient_address(self):
        person = self.env["ni.patient.related.person"].create(
            {"name": "Child", "patient_id": self.patient.id, "street": "Old street"}
        )
        person.action_copy_parent_address()
        self.assertEqual(person.street, "99 Moo 1")
        self.assertEqual(person.city, "Khlong Luang")
        self.assertEqual(person.zip, "12120")
        self.assertEqual(person.country_id, self.env.ref("base.th"))

    def test_copy_patient_address_empty(self):
        partner = self.env["res.partner"].create({"name": "No address"})
        patient = self.env["ni.patient"].create({"partner_id": partner.id})
        person = self.env["ni.patient.related.person"].create(
            {"name": "Child", "patient_id": patient.id, "street": "Old street"}
        )
        person.action_copy_parent_address()
        self.assertEqual(person.street, "Old street")
