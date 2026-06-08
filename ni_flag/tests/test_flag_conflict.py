#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestFlagConflict(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Conflict Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_AMB").id,
            }
        )
        cls.code_dnr = cls.env.ref("ni_flag.code_dnr")
        cls.code_fall = cls.env.ref("ni_flag.code_fall")
        cls.code_fall.conflict_code_ids = [(4, cls.code_dnr.id)]
        cls.obs_type = cls.env["ni.observation.type"].create(
            {"name": "Conflict Score", "code": "CONFLICT-SCORE", "value_type": "float"}
        )

    def _make_recommendation(self):
        observation = self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "type_id": self.obs_type.id,
                "value_float": 8.0,
            }
        )
        return self.env["ni.flag.recommendation"].create(
            {
                "name": "Conflict recommendation",
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "flag_code_id": self.code_fall.id,
                "rule_id": self.env["ni.flag.recommendation.rule"]
                .create(
                    {
                        "name": "Conflict rule",
                        "observation_type_id": self.obs_type.id,
                        "flag_code_id": self.code_fall.id,
                    }
                )
                .id,
                "source_observation_id": observation.id,
            }
        )

    def test_accept_conflicting_recommendation_returns_wizard(self):
        self.env["ni.flag"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "code_id": self.code_dnr.id,
            }
        )
        recommendation = self._make_recommendation()
        action = recommendation.action_accept()
        self.assertEqual(action["res_model"], "ni.flag.conflict.wizard")

    def test_conflict_wizard_replaces_existing_flag(self):
        conflicting_flag = self.env["ni.flag"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "code_id": self.code_dnr.id,
            }
        )
        recommendation = self._make_recommendation()
        wizard = self.env["ni.flag.conflict.wizard"].create(
            {"recommendation_id": recommendation.id}
        )
        wizard.action_confirm()
        conflicting_flag.invalidate_recordset(["status", "period_end"])
        self.assertEqual(conflicting_flag.status, "inactive")
        self.assertTrue(conflicting_flag.period_end)
        new_flag = self.env["ni.flag"].search(
            [
                ("patient_id", "=", self.patient.id),
                ("encounter_id", "=", self.encounter.id),
                ("code_id", "=", self.code_fall.id),
                ("status", "=", "active"),
            ]
        )
        self.assertEqual(len(new_flag), 1)

    def test_auto_apply_deactivates_conflicting_flags(self):
        conflicting_flag = self.env["ni.flag"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "code_id": self.code_dnr.id,
            }
        )
        recommendation = self._make_recommendation()
        recommendation.action_auto_apply()
        conflicting_flag.invalidate_recordset(["status", "period_end"])
        self.assertEqual(conflicting_flag.status, "inactive")
        self.assertTrue(conflicting_flag.period_end)
