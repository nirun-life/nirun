#  Copyright (c) 2026 NSTDA

from datetime import datetime, timedelta

from .common import TestEncounterAutoCloseCommon


class TestEncounterClassAutoClose(TestEncounterAutoCloseCommon):
    """Baseline behaviour of cron_auto_close(), with the company timezone
    pinned to UTC so results don't depend on local-midnight logic.
    Timezone-sensitive edge cases live in
    test_ni_encounter_class_auto_close_edge_cases.py."""

    def setUp(self):
        super().setUp()
        self._set_company_tz("UTC")

    def test_closes_encounter_past_offset(self):
        now = datetime(2026, 1, 10, 6, 0, 0)
        encounter = self._make_encounter(
            self.class_midnight, create_date=datetime(2026, 1, 8, 10, 0, 0)
        )
        self._run_cron(now)
        self.assertEqual(encounter.state, "finished")

    def test_keeps_encounter_within_offset(self):
        # The offset day boundary is end-of-day inclusive (see
        # _get_auto_close_reference_time), so the whole calendar day the
        # encounter was created on is protected - only strictly earlier
        # days are eligible to close.
        now = datetime(2026, 1, 10, 6, 0, 0)
        encounter = self._make_encounter(
            self.class_midnight, create_date=datetime(2026, 1, 10, 1, 0, 0)
        )
        self._run_cron(now)
        self.assertEqual(encounter.state, "in-progress")

    def test_ignores_disabled_class(self):
        now = datetime(2026, 1, 10, 6, 0, 0)
        encounter = self._make_encounter(
            self.class_disabled, create_date=datetime(2026, 1, 1, 0, 0, 0)
        )
        self._run_cron(now)
        self.assertEqual(encounter.state, "in-progress")

    def test_ignores_non_in_progress_state(self):
        now = datetime(2026, 1, 10, 6, 0, 0)
        encounter = self._make_encounter(
            self.class_midnight,
            state="draft",
            create_date=datetime(2026, 1, 1, 0, 0, 0),
        )
        self._run_cron(now)
        self.assertEqual(encounter.state, "draft")

    def test_hours_offset_uses_full_datetime_not_date(self):
        # Non-midnight branch compares full datetimes (now - offset), so it
        # is not affected by the UTC/date-only bug covered in the edge
        # case test file.
        now = datetime(2026, 1, 10, 12, 0, 0)
        kept = self._make_encounter(
            self.class_offset, create_date=now - timedelta(hours=5)
        )
        closed = self._make_encounter(
            self.class_offset, create_date=now - timedelta(hours=7)
        )
        self._run_cron(now)
        self.assertEqual(kept.state, "in-progress")
        self.assertEqual(closed.state, "finished")
