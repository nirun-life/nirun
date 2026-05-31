#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestFlag(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "Flag Test Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_AMB").id,
            }
        )

        cls.code_dnr = cls.env.ref("ni_flag.code_dnr")
        cls.code_fall = cls.env.ref("ni_flag.code_fall")

    def _make_flag(self, code, encounter=None):
        vals = {"patient_id": self.patient.id, "code_id": code.id}
        if encounter:
            vals["encounter_id"] = encounter.id
        return self.env["ni.flag"].create(vals)

    # ── ni.patient.flag_code_ids ───────────────────────────────────────────────

    def test_patient_compute_shows_patient_level(self):
        flag = self._make_flag(self.code_dnr)
        self.assertIn(self.code_dnr, self.patient.flag_code_ids)
        flag.unlink()

    def test_patient_compute_excludes_encounter_scoped(self):
        flag = self._make_flag(self.code_dnr, encounter=self.encounter)
        self.assertNotIn(self.code_dnr, self.patient.flag_code_ids)
        flag.unlink()

    def test_patient_inverse_add_creates_patient_level_flag(self):
        self.patient.flag_code_ids = [(4, self.code_dnr.id)]
        flag = self.env["ni.flag"].search(
            [("patient_id", "=", self.patient.id), ("code_id", "=", self.code_dnr.id)]
        )
        self.assertTrue(flag)
        self.assertFalse(flag.encounter_id)
        self.assertEqual(flag.status, "active")

    def test_patient_inverse_remove_deactivates_flag(self):
        flag = self._make_flag(self.code_fall)
        self.patient.flag_code_ids = [(3, self.code_fall.id)]
        self.assertEqual(flag.status, "inactive")
        self.assertTrue(flag.period_end)

    # ── ni.encounter.patient_flag_code_ids ────────────────────────────────────

    def test_encounter_patient_compute_shows_patient_level(self):
        flag = self._make_flag(self.code_dnr)
        self.assertIn(self.code_dnr, self.encounter.patient_flag_code_ids)
        flag.unlink()

    def test_encounter_patient_compute_excludes_encounter_scoped(self):
        flag = self._make_flag(self.code_dnr, encounter=self.encounter)
        self.assertNotIn(self.code_dnr, self.encounter.patient_flag_code_ids)
        flag.unlink()

    def test_encounter_patient_inverse_add_creates_patient_level(self):
        self.encounter.patient_flag_code_ids = [(4, self.code_dnr.id)]
        flag = self.env["ni.flag"].search(
            [("patient_id", "=", self.patient.id), ("code_id", "=", self.code_dnr.id)]
        )
        self.assertTrue(flag)
        self.assertFalse(flag.encounter_id, "Flag must not have encounter_id set")
        self.assertEqual(flag.status, "active")

    # ── ni.encounter.encounter_flag_code_ids ──────────────────────────────────

    def test_encounter_compute_shows_encounter_scoped(self):
        flag = self._make_flag(self.code_fall, encounter=self.encounter)
        self.assertIn(self.code_fall, self.encounter.encounter_flag_code_ids)
        flag.unlink()

    def test_encounter_compute_excludes_patient_level(self):
        flag = self._make_flag(self.code_fall)
        self.assertNotIn(self.code_fall, self.encounter.encounter_flag_code_ids)
        flag.unlink()

    def test_encounter_inverse_add_creates_encounter_scoped(self):
        self.encounter.encounter_flag_code_ids = [(4, self.code_fall.id)]
        flag = self.env["ni.flag"].search(
            [
                ("patient_id", "=", self.patient.id),
                ("encounter_id", "=", self.encounter.id),
                ("code_id", "=", self.code_fall.id),
            ]
        )
        self.assertTrue(flag)
        self.assertEqual(flag.encounter_id, self.encounter)
        self.assertEqual(flag.status, "active")

    def test_encounter_inverse_remove_deactivates_flag(self):
        flag = self._make_flag(self.code_fall, encounter=self.encounter)
        self.encounter.encounter_flag_code_ids = [(3, self.code_fall.id)]
        self.assertEqual(flag.status, "inactive")
        self.assertTrue(flag.period_end)
