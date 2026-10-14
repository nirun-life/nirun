#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestUom(common.TransactionCase):
    """Nirun units on the 19.0 UoM model (relative_uom_id / relative_factor)."""

    def uom(self, xmlid):
        return self.env.ref(f"ni_observation.{xmlid}")

    def test_reference_units(self):
        for xmlid in ("uom_%", "uom_kg_m3", "uom_mmHg", "uom_per_min", "uom_k_ul"):
            unit = self.uom(xmlid)
            self.assertFalse(unit.relative_uom_id, xmlid)
            self.assertEqual(unit.relative_factor, 1.0, xmlid)
            self.assertEqual(unit.factor, 1.0, xmlid)

    def test_relative_units(self):
        cases = [
            ("uom_mg_dl", "uom_kg_m3", 0.01),
            ("uom_m_ul", "uom_k_ul", 1000.0),
            ("uom_per_hour", "uom_per_min", 60.0),
        ]
        for xmlid, reference, relative_factor in cases:
            unit = self.uom(xmlid)
            self.assertEqual(unit.relative_uom_id, self.uom(reference), xmlid)
            self.assertAlmostEqual(unit.relative_factor, relative_factor)
        self.assertAlmostEqual(self.uom("uom_per_sec").relative_factor, 1 / 60)

    def test_conversion_unchanged(self):
        """Same results as the 16.0 factor-based data."""
        kg_m3, mg_dl = self.uom("uom_kg_m3"), self.uom("uom_mg_dl")
        self.assertAlmostEqual(kg_m3._compute_quantity(1, mg_dl, round=False), 100)
        self.assertAlmostEqual(mg_dl._compute_quantity(250, kg_m3, round=False), 2.5)
        k_ul, m_ul = self.uom("uom_k_ul"), self.uom("uom_m_ul")
        self.assertAlmostEqual(m_ul._compute_quantity(4.5, k_ul, round=False), 4500)

    def test_observation_unit(self):
        """Observation types keep their Nirun unit."""
        bp_s = self.env["ni.observation.type"].search([("code", "=", "bp-s")])
        self.assertEqual(bp_s.unit_id, self.uom("uom_mmHg"))
