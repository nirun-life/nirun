#  Copyright (c) 2026 NSTDA

from psycopg2 import IntegrityError

from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestPatientUnique(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.thailand = cls.env.ref("base.th")
        cls.company_2 = cls.env["res.company"].create({"name": "Second"})
        cls.patient = cls._patient()

    @classmethod
    def _patient(cls, identification_id="1104740100001", **vals):
        partner = cls.env["res.partner"].create({"name": "Unique"})
        return cls.env["ni.patient"].create(
            {
                "partner_id": partner.id,
                "company_id": cls.env.company.id,
                "nationality_id": cls.thailand.id,
                "identification_id": identification_id,
                **vals,
            }
        )

    def test_same_company_and_nationality(self):
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                self._patient()

    def test_write(self):
        other = self._patient(identification_id="1104740100002")
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            with self.env.cr.savepoint():
                other.identification_id = self.patient.identification_id
                other.flush_recordset()

    def test_other_company_or_nationality(self):
        self.assertTrue(self._patient(company_id=self.company_2.id))
        self.assertTrue(self._patient(nationality_id=self.env.ref("base.la").id))

    def test_without_identification(self):
        self.assertTrue(self._patient(identification_id=False))
        self.assertTrue(self._patient(identification_id=False))

    def test_stored(self):
        self.patient.partner_id.identification_id = "1104740100003"
        self.patient.flush_recordset()
        self.env.cr.execute(
            "SELECT identification_id FROM ni_patient WHERE id = %s", [self.patient.id]
        )
        self.assertEqual(self.env.cr.fetchone()[0], "1104740100003")
