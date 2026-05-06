#  Copyright (c) 2024 NSTDA

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestInverseValue(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        partner = cls.env["res.partner"].create({"name": "Test Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})

        cls.type_char = cls.env["ni.observation.type"].create(
            {"name": "Test Char Obs", "value_type": "char"}
        )
        cls.type_int = cls.env["ni.observation.type"].create(
            {"name": "Test Int Obs", "value_type": "int"}
        )
        cls.type_float = cls.env["ni.observation.type"].create(
            {"name": "Test Float Obs", "value_type": "float"}
        )
        cls.type_code_id = cls.env["ni.observation.type"].create(
            {"name": "Test Code Obs", "value_type": "code_id"}
        )
        cls.type_code_ids = cls.env["ni.observation.type"].create(
            {"name": "Test Multi-Code Obs", "value_type": "code_ids"}
        )

        cls.code_yes = cls.env["ni.observation.value.code"].create(
            {
                "name": "Yes",
                "code": "YES",
                "type_ids": [
                    (4, cls.type_code_id.id),
                    (4, cls.type_code_ids.id),
                ],
            }
        )
        cls.code_no = cls.env["ni.observation.value.code"].create(
            {
                "name": "No",
                "code": "NO",
                "type_ids": [(4, cls.type_code_ids.id)],
            }
        )

    def _make_ob(self, ob_type):
        return self.env["ni.observation"].create(
            {"patient_id": self.patient.id, "type_id": ob_type.id}
        )

    def test_char_sets_value_char(self):
        ob = self._make_ob(self.type_char)
        ob.value = "hello"
        self.assertEqual(ob.value_char, "hello")

    def test_int_sets_value_int_and_value_float(self):
        ob = self._make_ob(self.type_int)
        ob.value = "42"
        self.assertEqual(ob.value_int, 42)
        self.assertEqual(ob.value_float, 42.0)

    def test_int_truncates_decimal_string(self):
        ob = self._make_ob(self.type_int)
        ob.value = "42.5"
        self.assertEqual(ob.value_int, 42)

    def test_float_sets_value_float(self):
        ob = self._make_ob(self.type_float)
        ob.value = "3.5"
        self.assertAlmostEqual(ob.value_float, 3.5)

    def test_falsy_value_is_skipped(self):
        ob = self._make_ob(self.type_char)
        ob.value_char = "existing"
        ob.value = False
        # _inverse_value must not overwrite value_char when value is falsy
        self.assertEqual(ob.value_char, "existing")

    def test_code_id_matched_by_name(self):
        ob = self._make_ob(self.type_code_id)
        ob.value = "Yes"
        self.assertEqual(ob.value_code_id, self.code_yes)

    def test_code_id_matched_by_code(self):
        ob = self._make_ob(self.type_code_id)
        ob.value = "YES"
        self.assertEqual(ob.value_code_id, self.code_yes)

    def test_code_id_not_found_raises_validation_error(self):
        ob = self._make_ob(self.type_code_id)
        with self.assertRaises(ValidationError):
            ob.value = "Unknown Value"

    def test_code_ids_sets_multiple_codes(self):
        ob = self._make_ob(self.type_code_ids)
        ob.value = "Yes, No"
        self.assertIn(self.code_yes, ob.value_code_ids)
        self.assertIn(self.code_no, ob.value_code_ids)

    def test_code_ids_silently_ignores_unmatched(self):
        ob = self._make_ob(self.type_code_ids)
        ob.value = "Yes, Unknown"
        self.assertEqual(ob.value_code_ids, self.code_yes)
