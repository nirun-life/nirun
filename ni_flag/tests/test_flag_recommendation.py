#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestFlagRecommendation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Recommendation Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_AMB").id,
            }
        )
        cls.flag_code = cls.env.ref("ni_flag.code_fall")
        cls.obs_type = cls.env["ni.observation.type"].create(
            {"name": "Fall Score", "code": "FALL-SCORE", "value_type": "float"}
        )
        cls.interpretation = cls.env["ni.observation.interpretation"].create(
            {
                "name": "High Risk",
                "code": "HIGH-RISK",
                "display_class": "danger",
                "is_problem": True,
            }
        )
        cls.env["ni.observation.reference.range"].create(
            {
                "type_id": cls.obs_type.id,
                "low": 10.0,
                "high": 20.0,
                "interpretation_id": cls.interpretation.id,
            }
        )

    def test_rule_matches_observation_interpretation(self):
        rule = self.env["ni.flag.recommendation.rule"].create(
            {
                "name": "High fall score recommends fall risk",
                "observation_type_id": self.obs_type.id,
                "interpretation_id": self.interpretation.id,
                "flag_code_id": self.flag_code.id,
                "scope": "encounter",
                "mode": "recommend",
            }
        )
        observation = self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "type_id": self.obs_type.id,
                "value_float": 12.0,
            }
        )
        self.assertTrue(rule._matches_observation(observation))

    def test_observation_creates_pending_recommendation(self):
        self.env["ni.flag.recommendation.rule"].create(
            {
                "name": "High fall score recommends fall risk",
                "observation_type_id": self.obs_type.id,
                "interpretation_id": self.interpretation.id,
                "flag_code_id": self.flag_code.id,
                "scope": "encounter",
                "mode": "recommend",
            }
        )
        observation = self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "type_id": self.obs_type.id,
                "value_float": 12.0,
            }
        )
        recommendation = self.env["ni.flag.recommendation"].search(
            [("source_observation_id", "=", observation.id)]
        )
        self.assertEqual(len(recommendation), 1)
        self.assertEqual(recommendation.state, "pending")
        self.assertEqual(recommendation.flag_code_id, self.flag_code)
        self.assertFalse(
            self.env["ni.flag"].search(
                [
                    ("source_observation_id", "=", observation.id),
                    ("status", "=", "active"),
                ]
            )
        )

    def test_auto_apply_rule_creates_flag_with_evidence(self):
        self.env["ni.flag.recommendation.rule"].create(
            {
                "name": "Auto high fall score",
                "observation_type_id": self.obs_type.id,
                "interpretation_id": self.interpretation.id,
                "flag_code_id": self.flag_code.id,
                "scope": "encounter",
                "mode": "auto_apply",
            }
        )
        observation = self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "type_id": self.obs_type.id,
                "value_float": 12.0,
            }
        )
        flag = self.env["ni.flag"].search(
            [("source_observation_id", "=", observation.id), ("status", "=", "active")]
        )
        self.assertEqual(len(flag), 1)
        self.assertEqual(flag.origin, "auto_rule")

    def test_same_observation_rule_does_not_create_duplicate_recommendations(self):
        rule = self.env["ni.flag.recommendation.rule"].create(
            {
                "name": "No duplicate recommendation",
                "observation_type_id": self.obs_type.id,
                "interpretation_id": self.interpretation.id,
                "flag_code_id": self.flag_code.id,
                "scope": "encounter",
                "mode": "recommend",
            }
        )
        observation = self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "type_id": self.obs_type.id,
                "value_float": 12.0,
            }
        )
        observation.write({"value_float": 13.0})
        recommendations = self.env["ni.flag.recommendation"].search(
            [("source_observation_id", "=", observation.id), ("rule_id", "=", rule.id)]
        )
        self.assertEqual(len(recommendations), 1)

    def test_accept_recommendation_reuses_existing_active_flag(self):
        self.env["ni.flag"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "code_id": self.flag_code.id,
            }
        )
        observation = self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "type_id": self.obs_type.id,
                "value_float": 12.0,
            }
        )
        rule = self.env["ni.flag.recommendation.rule"].create(
            {
                "name": "Reuse active flag",
                "observation_type_id": self.obs_type.id,
                "flag_code_id": self.flag_code.id,
            }
        )
        recommendation = self.env["ni.flag.recommendation"].create(
            {
                "name": "Reuse active flag",
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "flag_code_id": self.flag_code.id,
                "rule_id": rule.id,
                "source_observation_id": observation.id,
            }
        )
        recommendation.action_accept()
        flags = self.env["ni.flag"].search(
            [
                ("patient_id", "=", self.patient.id),
                ("encounter_id", "=", self.encounter.id),
                ("code_id", "=", self.flag_code.id),
                ("status", "=", "active"),
            ]
        )
        self.assertEqual(len(flags), 1)
