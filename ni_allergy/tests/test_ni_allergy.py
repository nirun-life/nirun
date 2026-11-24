#  Copyright (c) 2026 NSTDA

from odoo.tests import TransactionCase


class TestAllergy(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["ni.patient"].create(
            {"partner_id": cls.env["res.partner"].create({"name": "Allergy P."}).id}
        )
        cls.code = cls.env["ni.allergy.code"].create(
            {"name": "Test Peanut", "code": "TPN", "category": "food"}
        )

    def test_create_single(self):
        allergy = self.env["ni.allergy"].create(
            {"patient_id": self.patient.id, "code_id": self.code.id}
        )
        self.assertEqual(allergy.name, "Test Peanut")

    def test_create_multi(self):
        other = self.env["ni.allergy.code"].create({"name": "Test Egg", "code": "TEG"})
        allergies = self.env["ni.allergy"].create(
            [
                {"patient_id": self.patient.id, "code_id": self.code.id},
                {"patient_id": self.patient.id, "code_id": other.id, "name": "Egg"},
            ]
        )
        self.assertEqual(allergies.mapped("name"), ["Test Peanut", "Egg"])

    def test_name(self):
        allergy = self.env["ni.allergy"].create(
            [
                {
                    "patient_id": self.patient.id,
                    "code_id": self.code.id,
                    "criticality": "high",
                }
            ]
        )

        def name(**context):
            return dict(allergy.with_context(**context).name_get())[allergy.id]

        self.assertEqual(name(), "Test Peanut")
        self.assertEqual(name(show_patient=True), "Allergy P. - Test Peanut")
        self.assertEqual(name(show_criticality=True), "Test Peanut[High]")
        self.assertEqual(name(show_state=True), "Test Peanut (Active)")

    def test_name_without_code(self):
        allergy = self.env["ni.allergy"].create(
            [{"patient_id": self.patient.id, "name": "Free text"}]
        )
        self.assertEqual(allergy.name_get(), [(allergy.id, "Free text")])
