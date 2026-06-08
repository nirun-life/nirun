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

    def test_flag_can_store_source_observation(self):
        obs_type = self.env["ni.observation.type"].create(
            {
                "name": "Flag Evidence Test",
                "code": "FLAG-EVIDENCE",
                "value_type": "float",
            }
        )
        observation = self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "type_id": obs_type.id,
                "value_float": 9.0,
            }
        )
        flag = self.env["ni.flag"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "code_id": self.code_fall.id,
                "source_observation_id": observation.id,
                "origin": "recommendation",
            }
        )
        self.assertEqual(flag.source_observation_id, observation)
        self.assertEqual(flag.origin, "recommendation")

    def test_manual_flag_origin_defaults_to_manual(self):
        flag = self._make_flag(self.code_dnr)
        self.assertEqual(flag.origin, "manual")

    def test_patient_action_manage_flags_opens_patient_manager(self):
        action = self.patient.action_manage_flags()
        expected_action = self.env.ref("ni_flag.ni_patient_flag_action")

        self.assertEqual(action["res_model"], "ni.flag")
        self.assertEqual(action["view_mode"], "kanban,tree,form")
        self.assertEqual(action["id"], expected_action.id)
        self.assertEqual(action["domain"], [("patient_id", "=", self.patient.id)])
        self.assertEqual(action["context"]["default_patient_id"], self.patient.id)
        self.assertEqual(action["context"]["search_default_group_state"], 1)
        self.assertNotIn("search_default_active", action["context"])

    def test_encounter_action_manage_flags_opens_encounter_manager(self):
        action = self.encounter.action_manage_flags()
        expected_action = self.env.ref("ni_flag.ni_encounter_flag_action")

        self.assertEqual(action["res_model"], "ni.flag")
        self.assertEqual(action["view_mode"], "kanban,tree,form")
        self.assertEqual(action["id"], expected_action.id)
        self.assertEqual(action["domain"], [("encounter_id", "=", self.encounter.id)])
        self.assertEqual(action["context"]["default_patient_id"], self.patient.id)
        self.assertEqual(action["context"]["default_encounter_id"], self.encounter.id)
        self.assertEqual(action["context"]["search_default_group_encounter"], 1)
        self.assertNotIn("search_default_active", action["context"])
