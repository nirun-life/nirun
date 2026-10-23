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
        cls.encounter = cls._create_encounter(cls.patient)
        cls.type = cls.env["ni.observation.type"].create(
            {
                "name": "Latest Test",
                "code": "test-latest",
                "value_type": "int",
                "min": 0,
                "max": 100,
            }
        )

    @classmethod
    def _create_encounter(cls, patient):
        return cls.env["ni.encounter"].create(
            {
                "patient_id": patient.id,
                "class_id": cls.env.ref("ni_patient.class_IMP").id,
                "period_start": fields.Datetime.now(),
            }
        )

    def _observe(self, value, occurrence, patient=None, encounter=None):
        patient = patient or self.patient
        if encounter is None:
            encounter = self.encounter
        return self.env["ni.observation"].create(
            {
                "patient_id": patient.id,
                "encounter_id": encounter.id,
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

    def _views(self):
        return (
            ("ni.patient.observation", "patient_id", self.patient),
            ("ni.encounter.observation", "encounter_id", self.encounter),
        )

    def test_later_occurrence_wins_over_higher_id(self):
        last = self._observe(1, "2025-01-02 08:00:00")
        self._observe(2, "2025-01-01 08:00:00")
        for model, field, record in self._views():
            self.assertEqual(self._latest(model, field, record).ids, [last.id])

    def test_newer_observation_without_value_is_ignored(self):
        last = self._observe(1, "2025-01-01 08:00:00")
        self._observe(0, "2025-01-02 08:00:00")
        for model, field, record in self._views():
            self.assertEqual(self._latest(model, field, record).ids, [last.id])

    def test_other_patient_does_not_hide_the_latest(self):
        partner = self.env["res.partner"].create({"name": "Latest Other Patient"})
        other_patient = self.env["ni.patient"].create({"partner_id": partner.id})
        other_encounter = self._create_encounter(other_patient)
        last = self._observe(1, "2025-01-01 08:00:00")
        self._observe(2, "2025-01-02 08:00:00", other_patient, other_encounter)
        for model, field, record in self._views():
            self.assertEqual(self._latest(model, field, record).ids, [last.id])

    def test_search_by_id_returns_only_the_latest(self):
        """The ORM reads these views by id, so a filter on id alone must
        still drop the rows that are not the latest of their group."""
        first = self._observe(1, "2025-01-01 08:00:00")
        last = self._observe(2, "2025-01-02 08:00:00")
        self.env.flush_all()
        for model, _field, _record in self._views():
            rows = self.env[model].search([("id", "in", [first.id, last.id])])
            self.assertEqual(rows.ids, [last.id])
            self.assertEqual(rows.read(["value_int"])[0]["value_int"], 2)

    def test_encounter_view_skips_observation_without_encounter(self):
        no_encounter = self._observe(
            1, "2025-01-01 08:00:00", encounter=self.env["ni.encounter"]
        )
        self.env.flush_all()
        domain = [("id", "=", no_encounter.id)]
        self.assertFalse(self.env["ni.encounter.observation"].search(domain))
        self.assertTrue(self.env["ni.patient.observation"].search(domain))

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
