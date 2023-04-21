#  Copyright (c) 2023 NSTDA

from odoo import fields
from odoo.tests.common import TransactionCase


class TestPatient(TransactionCase):
    def test_problem_code(self):
        codes = self.env["ni.condition.code"].create(
            [
                {"name": "__Heart Attack"},
                {"name": "__Hypertension"},
                {"name": "__Diabate Type I"},
                {"name": "__Diabate Type II"},
            ]
        )
        patients = self.env["ni.patient"]
        encounter = self.env["ni.encounter"]

        peter = patients.create(
            {
                "name": "Peter Parker",
                "condition_problem_code_ids": [
                    (4, codes[0].id, 0),
                    (4, codes[1].id, 0),
                ],
            }
        )
        self.assertEqual(2, len(peter.condition_ids))
        self.assertItemsEqual(
            [codes[0].id, codes[1].id], peter.condition_ids.mapped("code_id.id")
        )

        peter_enc = encounter.create(
            {
                "patient_id": peter.id,
                "class_id": self.ref("ni_patient.class_VR"),
                "period_start": fields.datetime.now(),
            }
        )

        self.assertEqual(2, len(peter.condition_ids))
        # self.assertEqual(0, len(peter_enc.condition_ids))

        peter_enc.write({"condition_problem_code_ids": [(4, codes[2].id, 0)]})
        self.assertEqual(3, len(peter.condition_ids))
        self.assertEqual(0, len(peter_enc.condition_ids))

        peter_enc.write({"problem_code_ids": [(4, codes[3].id, 0)]})
        self.assertEqual(4, len(peter.condition_ids))
        self.assertEqual(1, len(peter_enc.condition_ids))
