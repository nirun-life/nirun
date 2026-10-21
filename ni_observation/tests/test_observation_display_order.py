#  Copyright (c) 2026 NSTDA
"""The Observation tab lists one category's latest values in type order."""

from odoo import fields
from odoo.tests import common


class TestObservationDisplayOrder(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Order Test Patient"})
        cls.patient = cls.env["ni.patient"].create({"partner_id": partner.id})
        cls.encounter = cls.env["ni.encounter"].create(
            {
                "patient_id": cls.patient.id,
                "class_id": cls.env.ref("ni_patient.class_IMP").id,
                "period_start": fields.Datetime.now(),
            }
        )
        cls.category = cls.env["ni.observation.category"].create({"name": "Order Test"})
        # Created first, shown last: the order must follow the type sequence,
        # not the record ids.
        cls.type_last = cls._create_type("Order Test Last", "test-order-last", 20)
        cls.type_first = cls._create_type("Order Test First", "test-order-first", 10)
        for obs_type in (cls.type_last, cls.type_first):
            cls.env["ni.observation"].create(
                {
                    "patient_id": cls.patient.id,
                    "encounter_id": cls.encounter.id,
                    "type_id": obs_type.id,
                    "occurrence": "2025-01-01 08:00:00",
                    "value_int": 1,
                }
            )
        # The latest-observation models are SQL views: read them after the flush.
        cls.env.flush_all()
        cls.env.invalidate_all()

    @classmethod
    def _create_type(cls, name, code, sequence):
        return cls.env["ni.observation.type"].create(
            {
                "name": name,
                "code": code,
                "sequence": sequence,
                "category_id": cls.category.id,
                "value_type": "int",
                "min": 0,
                "max": 100,
            }
        )

    def test_patient_tab_follows_type_order(self):
        self.patient.observation_category_id = self.category
        self.assertEqual(
            self.patient.filtered_patient_observation_ids.type_id.ids,
            [self.type_first.id, self.type_last.id],
        )

    def test_encounter_tab_follows_type_order(self):
        self.encounter.write(
            {
                "observation_category_id": self.category.id,
                "observation_filter": "encounter",
            }
        )
        self.assertEqual(
            self.encounter.filtered_encounter_observation_ids.type_id.ids,
            [self.type_first.id, self.type_last.id],
        )
