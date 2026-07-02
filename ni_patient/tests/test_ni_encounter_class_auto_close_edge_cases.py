#  Copyright (c) 2026 NSTDA

from datetime import datetime, timedelta

from .common import TestEncounterAutoCloseCommon


class TestEncounterClassAutoCloseCutoffBoundary(TestEncounterAutoCloseCommon):
    """Minute-precision checks of the "<=" cutoff comparison itself, with
    the company timezone pinned to UTC so results don't depend on the
    local-midnight logic covered below."""

    def setUp(self):
        super().setUp()
        self._set_company_tz("UTC")

    def test_midnight_offset_cutoff_boundary_minute_precision(self):
        # rev is now built from an explicit end-of-day instant in the
        # company timezone (here UTC), so the boundary is the rollover
        # from 2026-01-09 23:59:59.999999 to 2026-01-10 00:00:00.
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


class TestEncounterClassAutoCloseLocalMidnight(TestEncounterAutoCloseCommon):
    """
    Regression coverage for nirun-life/nirun#102: cron_auto_close()'s
    midnight-offset mode used to key off UTC midnight unconditionally
    (via now.date()), so a company running ahead of UTC (e.g. Thailand,
    UTC+7) could keep an encounter open for up to 7 extra hours past its
    real local due time, then close it abruptly whenever the UTC date
    happened to roll over - a boundary with no local meaning.

    _get_auto_close_reference_time() now derives the day boundary from
    the encounter company's timezone (res.company.resource_calendar_id.tz,
    falling back to UTC). These tests pin a company on Asia/Bangkok and
    check the cutoff to the minute.
    """

    def setUp(self):
        super().setUp()
        self._set_company_tz("Asia/Bangkok")

    def test_flips_at_local_midnight_not_utc_midnight(self):
        # Encounter created 2026-01-01 12:00 Bangkok (UTC+7) = 05:00 UTC.
        # 1-day offset: eligible to close starting local midnight of
        # 2026-01-02, i.e. 2026-01-01 17:00 UTC.
        create_date = datetime(2026, 1, 1, 5, 0, 0)
        encounter = self._make_encounter(self.class_midnight, create_date=create_date)

        # One minute before local midnight: still open.
        self._run_cron(datetime(2026, 1, 1, 16, 59, 0))
        self.assertEqual(encounter.state, "in-progress")

        # One minute after local midnight: closes immediately - unlike
        # the pre-fix behaviour, which ignored the company timezone and
        # would only close 7 hours later, at UTC midnight.
        self._run_cron(datetime(2026, 1, 1, 17, 1, 0))
        self.assertEqual(encounter.state, "finished")

    def test_no_longer_waits_for_the_old_utc_rollover(self):
        # Same scenario: before the fix, this encounter only closed once
        # the UTC calendar date rolled over at 2026-01-02 00:00 UTC. It
        # now closes hours earlier, right after local midnight
        # (2026-01-01 17:00 UTC) - well before that old instant.
        create_date = datetime(2026, 1, 1, 5, 0, 0)
        encounter = self._make_encounter(self.class_midnight, create_date=create_date)

        self._run_cron(datetime(2026, 1, 1, 20, 0, 0))
        self.assertEqual(encounter.state, "finished")
