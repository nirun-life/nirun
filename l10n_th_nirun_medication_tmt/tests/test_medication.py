#  Copyright (c) 2021 Piruin P.

from odoo.tests import common


class MedicationTest(common.TransactionCase):
    def test_ingredient_strength(self):
        medication = self.env["ni.medication"]
        form = self.env["ni.medication.form"].search(
            [("name", "=", "film-coated tablet")]
        )
        unit = self.env["ni.quantity.unit"].search([("name", "=", "tablet")])
        med = medication.create(
            {
                "tpu_code": 113795,
                "name": "RASILEZ HCT",
                "manufacturer_name": "NOVARTIS PHARMA, GERMANY",
                "active_ingredient": "aliskiren + hydrochlorothiazide",
                "strength": "300 mg + 12.5 mg",
                "form": form.ids[0],
                "amount_denominator_unit": unit.ids[0],
            }
        )

        self.assertEqual(
            "RASILEZ HCT (NOVARTIS PHARMA, GERMANY) (aliskiren 300 mg + "
            "hydrochlorothiazide 12.5 mg) film-coated tablet, 1 tablet",
            med.fsn,
        )

        med.write({"active_ingredient": "aliskiren", "strength": "300 mg"})
        self.assertEqual(
            "RASILEZ HCT (NOVARTIS PHARMA, GERMANY) (aliskiren 300 mg) "
            "film-coated tablet, 1 tablet",
            med.fsn,
        )

    def test_no_ingredient_strength(self):
        medication = self.env["ni.medication"]
        form = self.env["ni.medication.form"].search(
            [("name", "=", "film-coated tablet")]
        )
        unit = self.env["ni.quantity.unit"].search([("name", "=", "tablet")])
        med = medication.create(
            {
                "tpu_code": 113795,
                "name": "RASILEZ HCT",
                "manufacturer_name": "NOVARTIS PHARMA, GERMANY",
                "form": form.ids[0],
                "amount_denominator_unit": unit.ids[0],
            }
        )
        self.assertEqual(
            "RASILEZ HCT (NOVARTIS PHARMA, GERMANY) film-coated tablet, 1 tablet",
            med.fsn,
        )
