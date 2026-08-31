#  Copyright (c) 2026 NSTDA

from odoo.tests import common


class TestNiPatientRating(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["ni.patient"].create({"name": "Rating Test Patient"})
        enc_class = cls.env["ni.encounter.class"].search([], limit=1)
        cls.enc1 = cls.env["ni.encounter"].create(
            {"patient_id": cls.patient.id, "class_id": enc_class.id}
        )
        cls.enc2 = cls.env["ni.encounter"].create(
            {"patient_id": cls.patient.id, "class_id": enc_class.id}
        )

    def test_patient_rating_aggregates_encounter_ratings(self):
        r1 = self.enc1.rating_apply(4, token=self.enc1._rating_get_access_token())
        r2 = self.enc2.rating_apply(2, token=self.enc2._rating_get_access_token())
        # rating_ids' inverse (parent_res_id) is a plain Integer, not a Many2one,
        # so the ORM can't auto-invalidate the cached One2many on create; force it.
        self.patient.invalidate_recordset()

        self.assertEqual(r1.parent_res_model, "ni.patient")
        self.assertEqual(r1.parent_res_id, self.patient.id)
        self.assertEqual(set(self.patient.rating_ids.ids), {r1.id, r2.id})
        self.assertEqual(self.patient.rating_count, 2)
        self.assertEqual(self.patient.rating_avg, 3.0)
