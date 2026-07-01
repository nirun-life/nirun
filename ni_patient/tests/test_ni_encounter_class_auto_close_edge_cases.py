#  Copyright (c) 2026 NSTDA

from datetime import datetime, timedelta

from .common import TestEncounterAutoCloseCommon


class TestEncounterClassAutoCloseCutoffBoundary(TestEncounterAutoCloseCommon):
    """Minute-precision checks of the "<=" cutoff comparison itself,
    independent of the timezone bug covered below."""

    def test_midnight_offset_cutoff_boundary_minute_precision(self):
        # rev = now.date() - 1 day = 2026-01-09, but a bare `date` compared
        # with "<=" is end-of-day inclusive in Odoo (osv/expression.py
        # turns it into `datetime.combine(rev, time.max)`), so the real
        # boundary is the rollover from 2026-01-09 23:59 to 2026-01-10
        # 00:00 - not "midnight" of 2026-01-09 itself.
        now = datetime(2026, 1, 10, 6, 0, 0)

        one_minute_before_rollover = self._make_encounter(
            self.class_midnight, create_date=datetime(2026, 1, 9, 23, 59, 0)
        )
        one_minute_after_rollover = self._make_encounter(
            self.class_midnight, create_date=datetime(2026, 1, 10, 0, 1, 0)
        )

        self._run_cron(now)

        self.assertEqual(
            one_minute_before_rollover.state,
            "finished",
            "still within the offset day, 1 minute before the day rolls over",
        )
        self.assertEqual(
            one_minute_after_rollover.state,
            "in-progress",
            "already the next day, 1 minute after the rollover, must stay open",
        )

    def test_hours_offset_cutoff_boundary_minute_precision(self):
        now = datetime(2026, 1, 10, 12, 0, 0)
        cutoff = now - timedelta(hours=6)  # class_offset: 6 hours

        before = self._make_encounter(
            self.class_offset, create_date=cutoff - timedelta(minutes=1)
        )
        at_cutoff = self._make_encounter(self.class_offset, create_date=cutoff)
        after = self._make_encounter(
            self.class_offset, create_date=cutoff + timedelta(minutes=1)
        )

        self._run_cron(now)

        self.assertEqual(before.state, "finished", "1 minute before cutoff must close")
        self.assertEqual(at_cutoff.state, "finished", "exact cutoff is inclusive (<=)")
        self.assertEqual(
            after.state, "in-progress", "1 minute after cutoff must stay open"
        )


class TestEncounterClassAutoCloseTimezoneBug(TestEncounterAutoCloseCommon):
    """
    cron_auto_close() reasons entirely in UTC: fields.Datetime.now() is
    UTC-naive, and the midnight branch keys off now.date(). No company or
    user timezone is applied anywhere, so the code's day boundary is always
    UTC midnight - never local midnight. For UTC+7 (Thailand), local
    midnight happens 7 hours before UTC midnight, so an encounter that has
    genuinely been open for a full local day can still be treated as
    "today" by the code for up to 7 more hours, then close abruptly the
    moment the UTC date rolls over - a boundary with no local meaning.

    These tests pin the exact instants where that shows up, down to the
    minute, since the cron's flakiness is a pure wall-clock artifact of
    when it happens to fire - not something tied to any particular
    encounter. See nirun-life/nirun#102.
    """

    def test_encounter_still_open_one_minute_after_it_should_have_closed_locally(self):
        # Encounter created 2026-01-01 12:00 Bangkok (UTC+7) = 05:00 UTC.
        # Local business rule (1 day offset): eligible to close starting
        # local midnight of 2026-01-02, i.e. 2026-01-01 17:00 UTC.
        create_date = datetime(2026, 1, 1, 5, 0, 0)
        encounter = self._make_encounter(self.class_midnight, create_date=create_date)

        # One minute before the local boundary: correctly still open.
        self._run_cron(datetime(2026, 1, 1, 16, 59, 0))
        self.assertEqual(encounter.state, "in-progress")

        # One minute after the local boundary - a full local day has now
        # elapsed since creation, so this should close. But the UTC
        # calendar date is still "2026-01-01" (UTC midnight is still 7
        # hours away), so the code's cutoff hasn't moved and it stays
        # open. This documents the bug; flip to "finished" once a
        # timezone-aware cutoff is implemented.
        self._run_cron(datetime(2026, 1, 1, 17, 1, 0))
        self.assertEqual(encounter.state, "in-progress")

    def test_close_decision_flips_on_a_utc_rollover_one_minute_apart(self):
        # Same encounter as above, followed forward: nothing about it, or
        # about elapsed local time, changes meaningfully between these two
        # cron runs - only the UTC calendar date ticks over, 1 minute
        # apart. That alone flips the outcome, a full 7 hours after the
        # true local boundary (2026-01-01 17:00 UTC, see test above) had
        # already passed.
        create_date = datetime(2026, 1, 1, 5, 0, 0)
        encounter = self._make_encounter(self.class_midnight, create_date=create_date)

        self._run_cron(datetime(2026, 1, 1, 23, 59, 0))
        self.assertEqual(encounter.state, "in-progress")

        self._run_cron(datetime(2026, 1, 2, 0, 0, 0))
        self.assertEqual(encounter.state, "finished")
