#  Copyright (c) 2025 NSTDA

from odoo.tests import TransactionCase


class TestDosageTiming(TransactionCase):
    """ni.medication.dosage timing must resolve to the HL7 FHIR
    EventTiming codes (ni.timing.event) and Timing.repeat fields
    (ni.timing.timing) that ni_timing already models."""

    def setUp(self):
        super().setUp()
        self.Dosage = self.env["ni.medication.dosage"]

    def _when_codes(self, dosage):
        dosage._update_timing_when()
        return set(dosage.timing_id.when.mapped("code"))

    def test_before_breakfast(self):
        dosage = self.Dosage.create(
            {
                "timing_type": "meal",
                "meal_timing": "AC",
                "meal_period_ids": [
                    (6, 0, [self.ref("ni_medication.meal_period_breakfast")])
                ],
            }
        )
        self.assertEqual(self._when_codes(dosage), {"ACM"})

    def test_with_lunch(self):
        dosage = self.Dosage.create(
            {
                "timing_type": "meal",
                "meal_timing": "C",
                "meal_period_ids": [
                    (6, 0, [self.ref("ni_medication.meal_period_lunch")])
                ],
            }
        )
        self.assertEqual(self._when_codes(dosage), {"CD"})

    def test_after_dinner(self):
        dosage = self.Dosage.create(
            {
                "timing_type": "meal",
                "meal_timing": "PC",
                "meal_period_ids": [
                    (6, 0, [self.ref("ni_medication.meal_period_dinner")])
                ],
            }
        )
        self.assertEqual(self._when_codes(dosage), {"PCV"})

    def test_before_sleep_is_not_prefixed_with_meal_timing(self):
        # HS is its own EventTiming code; there is no "ACHS"/"PCHS"/"CHS"
        dosage = self.Dosage.create(
            {
                "timing_type": "meal",
                "meal_timing": "AC",
                "meal_period_ids": [
                    (6, 0, [self.ref("ni_medication.meal_period_beforesleep")])
                ],
            }
        )
        self.assertEqual(self._when_codes(dosage), {"HS"})

    def test_before_meals_and_before_sleep_combined(self):
        dosage = self.Dosage.create(
            {
                "timing_type": "meal",
                "meal_timing": "AC",
                "meal_period_ids": [
                    (
                        6,
                        0,
                        [
                            self.ref("ni_medication.meal_period_breakfast"),
                            self.ref("ni_medication.meal_period_dinner"),
                            self.ref("ni_medication.meal_period_beforesleep"),
                        ],
                    )
                ],
            }
        )
        self.assertEqual(self._when_codes(dosage), {"ACM", "ACV", "HS"})

    def test_period_timing(self):
        dosage = self.Dosage.create(
            {
                "timing_type": "period",
                "period_ids": [
                    (
                        6,
                        0,
                        [
                            self.ref("ni_medication.period_morning"),
                            self.ref("ni_medication.period_evening"),
                        ],
                    )
                ],
            }
        )
        self.assertEqual(self._when_codes(dosage), {"MORN", "EVE"})

    def test_offset_only_applies_when_not_with_meal(self):
        # FHIR Timing.repeat: an offset requires an event other than
        # "with meal" (C/CM/CD/CV) - see ni.timing.timing.check_timeofday_when
        dosage = self.Dosage.create(
            {
                "timing_type": "meal",
                "meal_timing": "C",
                "meal_offset": 30,
                "meal_period_ids": [
                    (6, 0, [self.ref("ni_medication.meal_period_breakfast")])
                ],
            }
        )
        dosage._update_timing_when()
        self.assertEqual(dosage.timing_id.offset, 0)

        dosage.meal_timing = "AC"
        dosage._update_timing_when()
        self.assertEqual(dosage.timing_id.offset, 30)

    def test_conventional_template_sets_fhir_repeat_fields(self):
        # ni.timing.template.BID: HL7 GTS "BID" == FHIR Timing.repeat
        # frequency=2, period=1, periodUnit=day
        dosage = self.Dosage.create({"timing_tmpl_id": self.ref("ni_timing.BID")})
        self.assertEqual(dosage.timing_frequency, 2)
        self.assertEqual(dosage.timing_period, 1)
        self.assertEqual(dosage.timing_period_unit, "day")
