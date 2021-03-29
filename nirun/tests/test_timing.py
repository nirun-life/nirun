#  Copyright (c) 2021 Piruin P.
from odoo.tests import TransactionCase

_timing_name = [
    ("Every 8 hours", 1, None, 8, None, "hour"),
    ("Every 7 hours", 1, None, 7, None, "hour"),
    ("3 times every day", 3, None, 1, None, "day"),
    ("Every 3-4 hours", 1, None, 3, 4, "hour"),
    ("1-2 times every day", 1, 2, 1, None, "day"),
]


class TestTiming(TransactionCase):
    def test_timing_name(self):
        timing = self.env["ni.timing"]
        for test in _timing_name:
            time = timing.create(
                {
                    "frequency": test[1],
                    "frequency_max": test[2],
                    "period": test[3],
                    "period_max": test[4],
                    "period_unit": test[5],
                }
            )
            self.assertEqual(test[0], time.name)

    def test_day_of_week(self):
        timing = self.env["ni.timing"]
        time = timing.create(
            {
                "frequency": 1,
                "period": 1,
                "period_unit": "day",
                "day_of_week": [
                    (0, 0, {"value": "Mon"}),
                    (0, 0, {"value": "Wed"}),
                    (0, 0, {"value": "Fri"}),
                ],
            }
        )
        self.assertEqual("Mon, wed, fri", time.name)
