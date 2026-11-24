#  Copyright (c) 2026 NSTDA

from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase


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

    def test_create_new_partner(self):
        relationship = self.env.ref("ni_related_person.REL_MTH")
        with Form(self.patient) as form:
            with form.related_person_ids.new() as line:
                line.name = "Mother"
                line.relationship_ids.add(relationship)
                line.phone = "0210000000"
                line.mobile = "0810000000"
        person = self.patient.related_person_ids
        self.assertEqual(person.partner_id.name, "Mother")
        self.assertEqual(person.partner_id.mobile, "0810000000")
        self.assertEqual(person.relationship_ids, relationship)
        self.assertEqual(person.display_name, "Mother")
        self.assertEqual(self.patient.related_person_count, 1)

    def test_create_existing_partner(self):
        partner = self.env["res.partner"].create({"name": "Existing contact"})
        count = self.env["res.partner"].search_count([])
        person = self.env["ni.patient.related.person"].create(
            {"partner_id": partner.id, "patient_id": self.patient.id}
        )
        self.assertEqual(person.name, "Existing contact")
        self.assertEqual(self.env["res.partner"].search_count([]), count)

    def test_default_patient(self):
        person = (
            self.env["ni.patient.related.person"]
            .with_context(active_model="ni.patient", active_id=self.patient.id)
            .create({"name": "From the patient"})
        )
        self.assertEqual(person.patient_id, self.patient)

    def test_not_related_to_themselves(self):
        with self.assertRaises(UserError):
            self.env["ni.patient.related.person"].create(
                {
                    "partner_id": self.patient.partner_id.id,
                    "patient_id": self.patient.id,
                }
            )

    def test_title_and_mobile(self):
        title = self.env["res.partner.title"].create({"name": "Test title"})
        with Form(self.patient) as form:
            with form.related_person_ids.new() as line:
                line.name = "Father"
                line.relationship_ids.add(self.env.ref("ni_related_person.REL_FTH"))
                line.title_id = title
                line.mobile = "0810000001"
        person = self.patient.related_person_ids
        person.invalidate_recordset()
        self.assertEqual(person.title_id, title)
        self.assertEqual(person.partner_id.title_id, title)
        self.assertEqual(person.mobile, "0810000001")
        self.assertEqual(person.partner_id.mobile, "0810000001")
