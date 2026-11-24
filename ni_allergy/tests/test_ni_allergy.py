#  Copyright (c) 2026 NSTDA

from datetime import datetime

from psycopg2 import IntegrityError

from odoo.exceptions import UserError
from odoo.tests import TransactionCase
from odoo.tools import mute_logger


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
            return allergy.with_context(**context).display_name

        self.assertEqual(name(), "Test Peanut")
        self.assertEqual(name(show_patient=True), "Allergy P. - Test Peanut")
        self.assertEqual(name(show_criticality=True), "Test Peanut[High]")
        self.assertEqual(name(show_state=True), "Test Peanut (Active)")
        allergy.action_resolve()
        self.assertEqual(name(show_state=True), "Test Peanut (Resolved)")

    def test_name_without_code(self):
        allergy = self.env["ni.allergy"].create(
            [{"patient_id": self.patient.id, "name": "Free text"}]
        )
        self.assertEqual(allergy.display_name, "Free text")
        self.assertEqual(
            allergy.with_context(show_criticality=True).display_name, "Free text"
        )

    def test_unique_code_per_patient(self):
        vals = {"patient_id": self.patient.id, "code_id": self.code.id}
        self.env["ni.allergy"].create(vals)
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            self.env["ni.allergy"].create(vals)

    def test_last_occurrence(self):
        allergies = self.env["ni.allergy"].create(
            [
                {
                    "patient_id": self.patient.id,
                    "code_id": self.code.id,
                    "reaction_ids": [
                        (0, 0, {"onset": "2026-01-01 01:00:00"}),
                        (0, 0, {"onset": "2026-03-01 01:00:00"}),
                    ],
                },
                {"patient_id": self.patient.id, "name": "No reaction"},
            ]
        )
        self.assertEqual(
            allergies.mapped("last_occurrence"), [datetime(2026, 3, 1, 1), False]
        )
        self.assertEqual(allergies.mapped("reaction_count"), [2, 0])

    def test_patient_allergy_codes(self):
        other = self.env["ni.allergy.code"].create({"name": "Test Egg", "code": "TEG"})
        self.patient.allergy_code_ids = self.code | other
        self.assertEqual(self.patient.allergy_ids.code_id, self.code | other)
        self.assertEqual(self.patient.allergy_count, 2)
        self.patient.allergy_code_ids = other
        self.assertEqual(self.patient.allergy_ids.code_id, other)

    def test_patient_allergy_codes_from_encounter(self):
        encounter = self.env["ni.encounter"].create(
            {
                "patient_id": self.patient.id,
                "class_id": self.env.ref("ni_patient.class_AMB").id,
            }
        )
        self.patient.with_context(
            active_model="ni.encounter", active_id=encounter.id
        ).allergy_code_ids = self.code
        self.assertEqual(self.patient.allergy_ids.encounter_id, encounter)

    def test_actions(self):
        self.env["ni.allergy"].create({"patient_id": self.patient.id, "name": "One"})
        action = self.patient.action_view_allergy()
        self.assertEqual(action["context"]["default_patient_id"], self.patient.id)
        self.assertEqual(action["domain"], [("patient_id", "=", self.patient.id)])
        self.assertEqual(self.patient.action_add_allergy()["target"], "new")

    def test_identified_needs_a_record(self):
        patient = self.patient.with_context(active_model="ni.patient")
        with self.assertRaises(UserError):
            patient.allergy = "identified"
