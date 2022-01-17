#  Copyright (c) 2021 Piruin P.
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tools.date_utils import datetime, get_timedelta

_timing_name = [
    ("Every 8 hours", 1, 0, 8, 0, "hour", 0, 0, 0),
    ("Every 7 hours", 1, 0, 7, 0, "hour", 0, 0, 0),
    ("3 times every day", 3, 0, 1, 0, "day", 0, 0, 0),
    ("Every 4-6 hours", 1, 0, 4, 6, "hour", 0, 0, 0),
    ("1-2 times every day", 1, 2, 1, 0, "day", 0, 0, 0),
    ("Every 21 days for 1 hour", 1, 0, 21, 0, "day", 1, 0, "hour"),
    ("Every 2 days for 10-15 minutes", 1, 0, 2, 0, "day", 10, 15, "minute"),
]


class TestTiming(TransactionCase):
    def setUp(self):
        super().setUp()
        self.timing = self.env["ni.timing"]

    def test_timing_name(self):
        for test in _timing_name:
            time = self.timing.create(
                {
                    "frequency": test[1],
                    "frequency_max": test[2],
                    "period": test[3],
                    "period_max": test[4],
                    "period_unit": test[5],
                    "duration": test[6],
                    "duration_max": test[7],
                    "duration_unit": test[8],
                }
            )
            self.assertEqual(test[0], time.name)

    def test_day_of_week(self):
        time = self.timing.create(
            {
                "frequency": 1,
                "period": 1,
                "period_unit": "week",
                "day_of_week": [
                    (
                        6,
                        0,
                        [
                            self.ref("nirun.Mon"),
                            self.ref("nirun.Wed"),
                            self.ref("nirun.Fri"),
                        ],
                    )
                ],
            }
        )
        self.assertEqual("Monday, wednesday, friday", time.name)

        time.update({"when": [(4, self.ref("nirun.MORN"))]})
        time._compute_name()
        self.assertEqual("Monday, wednesday, friday morning", time.name)

    def test_offset_when(self):
        with self.assertRaises(ValidationError):
            self.timing.create(
                {
                    "offset": 30,
                    "when": [(6, 0, [self.ref("nirun.CM"), self.ref("nirun.CV")])],
                }
            )

        time = self.timing.create(
            {
                "frequency": 1,
                "period": 1,
                "period_unit": "day",
                "offset": 30,
                "when": [(6, 0, [self.ref("nirun.ACM"), self.ref("nirun.ACV")])],
            }
        )
        self.assertEqual("Every day 30 min before breakfast, before dinner", time.name)

    def test_complex(self):
        time = self.timing.create(
            {
                "frequency": 3,
                "period": 1,
                "period_unit": "day",
                "offset": 30,
                "when": [(4, self.ref("nirun.AC"))],
            }
        )
        self.assertEqual("3 times every day 30 min before a meal", time.name)

    def test_garbage_collect(self):
        timing = self.timing.create(
            {
                "name": "3 times a day",
                "create_date": datetime.utcnow() - get_timedelta(2, "day"),
                "write_date": datetime.utcnow() - get_timedelta(2, "day"),
            }
        )
        self.timing.garbage_collect()

        self.assertFalse(self.timing.search([("id", "=", timing.id)]))
