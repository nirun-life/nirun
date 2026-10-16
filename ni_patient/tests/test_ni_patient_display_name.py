#  Copyright (c) 2026 NSTDA
"""Display names of patients, encounters and locations (decision D1, #137).

Since 17.0 ``display_name`` comes from ``_compute_display_name``; the patient must
show its name, never its identifier (HN), unless a context key asks for more.
"""

from odoo.tests import TransactionCase


class TestDisplayName(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create(
            {
                "name": "Display Patient",
                "gender": "female",
                "identification_id": "1234567890123",
                "age": 40,
            }
        )
        cls.patient = cls.env["ni.patient"].create(
            {"partner_id": partner.id, "identifier": "HN-DISPLAY-1"}
        )
        cls.enc_class = cls.env["ni.encounter.class"].create(
            {"name": "Display Class", "code": "DSP"}
        )
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.enc_class.id,
                "identifier": "EN-DISPLAY-1",
            }
        )
        cls.building = cls.env["ni.location"].create({"name": "Building A"})
        cls.ward = cls.env["ni.location"].create(
            {"name": "Ward 1", "alias": "W1", "parent_id": cls.building.id}
        )

    def test_patient_default_is_name(self):
        self.assertEqual(self.patient.display_name, "Display Patient")

    def test_patient_context_keys(self):
        patient = self.patient
        self.assertEqual(
            patient.with_context(show_identifier=True).display_name,
            "HN-DISPLAY-1  Display Patient",
        )
        self.assertEqual(
            patient.with_context(show_identification_id=True).display_name,
            "Display Patient (1234567890123)",
        )
        self.assertEqual(
            patient.with_context(show_age=True).display_name, "Display Patient (40Y)"
        )
        self.assertEqual(
            patient.with_context(show_gender_age=True).display_name,
            "Display Patient\nFemale, 40 years old",
        )

    def test_patient_name_search(self):
        Patient = self.env["ni.patient"]
        for term in ("Display Patient", "HN-DISPLAY-1", "1234567890123"):
            ids = [pid for pid, _name in Patient.name_search(term)]
            self.assertIn(self.patient.id, ids, term)

    def test_encounter_display_name(self):
        encounter = self.encounter
        self.assertEqual(encounter.display_name, encounter.name)
        self.assertEqual(
            encounter.with_context(show_class=True).display_name,
            f"{encounter.name}/DSP",
        )
        self.assertEqual(
            encounter.with_context(show_patient=True).display_name,
            f"{encounter.name} Display Patient",
        )

    def test_encounter_name_search_by_patient(self):
        ids = [eid for eid, _name in self.env["ni.encounter"].name_search("Display")]
        self.assertIn(self.encounter.id, ids)

    def test_location_display_name(self):
        ward = self.ward
        self.assertEqual(ward.display_name, "Ward 1 (W1)")
        self.assertEqual(
            ward.with_context(location_display="short").display_name, "Ward 1"
        )
        self.assertEqual(
            ward.with_context(show_parent=True).display_name, "Building A, Ward 1 (W1)"
        )
        self.assertEqual(ward.full_name, "Building A, Ward 1 (W1)")
