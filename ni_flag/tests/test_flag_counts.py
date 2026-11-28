#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestFlagCounts(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patients = cls.env["ni.patient"].create(
            [
                {"partner_id": cls.env["res.partner"].create({"name": f"Count {i}"}).id}
                for i in range(2)
            ]
        )
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patients[0].id,
                "class_id": cls.env.ref("ni_patient.class_AMB").id,
            }
        )
        cls.code = cls.env.ref("ni_flag.code_fall")

    def test_patient_count_counts_each_patient_once(self):
        Flag = self.env["ni.flag"]
        before = self.code.patient_count
        Flag.create({"patient_id": self.patients[0].id, "code_id": self.code.id})
        Flag.create(
            {
                "patient_id": self.patients[0].id,
                "encounter_id": self.encounter.id,
                "code_id": self.code.id,
            }
        )
        Flag.create({"patient_id": self.patients[1].id, "code_id": self.code.id})
        inactive = Flag.create(
            {"patient_id": self.patients[1].id, "code_id": self.code.id}
        )
        inactive.action_inactive()
        self.code.invalidate_recordset(["patient_count"])
        self.assertEqual(self.code.patient_count, before + 2)

    def test_pending_recommendation_count(self):
        obs_type = self.env["ni.observation.type"].create(
            {"name": "Count score", "code": "COUNT-SCORE", "value_type": "float"}
        )
        rule = self.env["ni.flag.recommendation.rule"].create(
            {
                "name": "Any score",
                "observation_type_id": obs_type.id,
                "flag_code_id": self.code.id,
            }
        )
        for value in (1.0, 2.0):
            self.env["ni.observation"].create(
                {
                    "patient_id": self.patients[0].id,
                    "encounter_id": self.encounter.id,
                    "type_id": obs_type.id,
                    "value_float": value,
                }
            )
        recommendations = self.env["ni.flag.recommendation"].search(
            [("rule_id", "=", rule.id)]
        )
        self.assertEqual(len(recommendations), 2)
        self.assertEqual(self.encounter.pending_flag_recommendation_count, 2)
        recommendations[0].action_dismiss()
        self.encounter.invalidate_recordset(["pending_flag_recommendation_count"])
        self.assertEqual(self.encounter.pending_flag_recommendation_count, 1)
        self.assertIn(
            self.encounter,
            self.env["ni.encounter"].search(
                [("pending_flag_recommendation_count", ">", 0)]
            ),
        )

    def test_manage_flags_action(self):
        action = self.encounter.with_context(lang="en_US").action_manage_flags()
        self.assertEqual(action["res_model"], "ni.flag")
        self.assertEqual(action["domain"], [("encounter_id", "=", self.encounter.id)])
        self.assertEqual(action["context"]["default_encounter_id"], self.encounter.id)
        action = self.patients[0].action_manage_flags()
        self.assertEqual(action["context"]["default_patient_id"], self.patients[0].id)
