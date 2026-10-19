#  Copyright (c) 2026 NSTDA
"""The latest-observation views pick one row per type, the same on every query."""

from odoo import fields
from odoo.tests import common


class TestLatestObservation(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Latest Test Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_IMP").id,
                "period_start": fields.Datetime.now(),
            }
        )
        cls.type = cls.env["ni.observation.type"].create(
            {
                "name": "Latest Test",
                "code": "test-latest",
                "value_type": "int",
                "min": 0,
                "max": 100,
            }
        )

    def _observe(self, value, occurrence):
        return self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "type_id": self.type.id,
                "occurrence": occurrence,
                "value_int": value,
            }
        )

    def _latest(self, model, field, record):
        self.env.flush_all()
        self.env.invalidate_all()
        return self.env[model].search(
            [(field, "=", record.id), ("type_id", "=", self.type.id)]
        )

    def test_latest_is_the_last_occurrence(self):
        self._observe(1, "2025-01-01 08:00:00")
        last = self._observe(2, "2025-01-02 08:00:00")
        for model, field, record in (
            ("ni.patient.observation", "patient_id", self.patient),
            ("ni.encounter.observation", "encounter_id", self.encounter),
        ):
            self.assertEqual(self._latest(model, field, record).ids, [last.id])

    def test_same_occurrence_picks_the_last_record(self):
        """Two observations of a type at the same time, as created in one
        transaction: the view must not return a different row on the next query,
        or the patient and encounter forms fail to read it."""
        self._observe(1, "2025-01-01 08:00:00")
        last = self._observe(2, "2025-01-01 08:00:00")
        for model, field, record in (
            ("ni.patient.observation", "patient_id", self.patient),
            ("ni.encounter.observation", "encounter_id", self.encounter),
        ):
            latest = self._latest(model, field, record)
            self.assertEqual(latest.ids, [last.id])
            self.assertEqual(latest.value_int, 2)
        # The patient form reads the one2many, then its rows by id: both must agree.
        rows = self.patient.patient_observation_ids.filtered(
            lambda o: o.type_id == self.type
        )
        self.assertEqual(rows.mapped("value_int"), [2])

    def test_compute_observation_on_many_rows(self):
        """Each latest row computes its own observation and history, also when
        several rows are read together."""
        other_type = self.type.copy({"name": "Latest Test 2", "code": "test-latest-2"})
        first = self._observe(1, "2025-01-01 08:00:00")
        last = self._observe(2, "2025-01-02 08:00:00")
        other = self.env["ni.observation"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "type_id": other_type.id,
                "occurrence": "2025-01-02 08:00:00",
                "value_int": 3,
            }
        )
        self.env.flush_all()
        self.env.invalidate_all()
        rows = self.env["ni.patient.observation"].search(
            [
                ("patient_id", "=", self.patient.id),
                ("type_id", "in", (self.type | other_type).ids),
            ]
        )
        self.assertEqual(len(rows), 2)
        by_type = {row.type_id: row for row in rows}
        self.assertEqual(by_type[self.type].observation_id, last)
        self.assertEqual(by_type[other_type].observation_id, other)
        self.assertEqual(by_type[self.type].history_ids, last.history_ids)
        self.assertIn(first, by_type[self.type].history_ids)
        self.assertEqual(by_type[other_type].history_count, len(other.history_ids))
