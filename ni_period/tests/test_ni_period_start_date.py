#  Copyright (c) 2026 NSTDA

import importlib.util
from datetime import date, datetime
from pathlib import Path

from odoo_test_helper import FakeModelLoader

from odoo.tests import TransactionCase

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "migrations"
    / "16.0.0.1.1"
    / "end-migration.py"
)


def _load_script():
    spec = importlib.util.spec_from_file_location("ni_period_end_migration", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestPeriodStartDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .models import PeriodOwnDateTest, PeriodTest

        cls.loader.update_registry((PeriodTest, PeriodOwnDateTest))
        cls.Period = cls.env["ni.period.test"]
        cls.PeriodOwn = cls.env["ni.period.own.date.test"]

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def _set_start_date_to_creation_day(self, record):
        """Write what the old default stored: the day the record was created."""
        self.env.flush_all()
        self.env.cr.execute(
            f'UPDATE "{record._table}" SET period_start_date = create_date::date '
            "WHERE id = %s",
            (record.id,),
        )
        record.invalidate_recordset(["period_start_date"])

    def _start_date(self, record):
        self.env.flush_all()
        self.env.cr.execute(
            f'SELECT period_start_date FROM "{record._table}" WHERE id = %s',
            (record.id,),
        )
        return self.env.cr.fetchone()[0]

    def test_period_start_date_follows_period_start_on_create(self):
        """Records created from code (import, RPC) get the start date of their
        period_start, not today."""
        record = self.Period.create({"period_start": datetime(2025, 3, 1, 3, 0)})
        self.assertEqual(record.period_start_date, date(2025, 3, 1))

    def test_end_migration_repairs_start_dates(self):
        start = datetime(2025, 3, 1, 3, 0)
        wrong = self.Period.create({"period_start": start})
        self._set_start_date_to_creation_day(wrong)
        date_mode = self.Period.create({"period_mode": "date", "period_start": start})
        self._set_start_date_to_creation_day(date_mode)
        correct = self.Period.create({"period_start": start})
        own = self.PeriodOwn.create({"period_start": start})
        self._set_start_date_to_creation_day(own)
        creation_day = self._start_date(wrong)
        self.assertNotEqual(creation_day, date(2025, 3, 1))

        with self.assertLogs("ni_period_end_migration", "INFO") as logs:
            _load_script().migrate(self.env.cr, "16.0.0.1.0")

        # 1. a datetime-mode row holding its creation day is fixed
        self.assertEqual(self._start_date(wrong), date(2025, 3, 1))
        self.assertEqual(wrong.period_start_date, date(2025, 3, 1))
        # 2. a date-mode row with a deliberate mismatch is left alone
        self.assertEqual(self._start_date(date_mode), creation_day)
        # 3. a row that is already correct is left alone
        self.assertEqual(self._start_date(correct), date(2025, 3, 1))
        # 4. a model that defines its own field is skipped
        self.assertEqual(self._start_date(own), creation_day)
        self.assertEqual(
            logs.output,
            [
                "INFO:ni_period_end_migration:ni_period: fixed period_start_date "
                "on 1 ni.period.test rows"
            ],
        )

    def test_end_migration_skips_a_fresh_install(self):
        wrong = self.Period.create({"period_start": datetime(2025, 3, 1, 3, 0)})
        self._set_start_date_to_creation_day(wrong)
        _load_script().migrate(self.env.cr, None)
        self.assertNotEqual(self._start_date(wrong), date(2025, 3, 1))
