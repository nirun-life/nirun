#  Copyright (c) 2021 Piruin P.

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError

from .common import TestPatientCommon


class TestPatientEncounter(TestPatientCommon):
    def setUp(self):
        super(TestPatientEncounter, self).setUp()
        self.miss_glenda = self.ref("nirun_patient.mrs_glenda")
        self.care_manager = self.ref("base.res_partner_address_1")

    def test_compute_start(self):
        encounter = self.env["ni.encounter"].with_user(self.patient_admin)
        encounter = encounter.create({"patient_id": self.miss_glenda})
        episode = self.env["ni.care.episode"].with_user(self.patient_admin)

        ep1 = episode.create(
            {
                "encounter_id": encounter.id,
                "period_start": fields.date.today() - relativedelta(years=2),
                "period_end": fields.date.today() - relativedelta(years=1),
                "care_manager": self.care_manager.id,
            }
        )
        encounter.update({"episode_ids": [(4, ep1.id)]})
        self.assertEqual(encounter.period_start, ep1.period_start)

        ep2 = episode.create(
            {
                "encounter_id": encounter.id,
                "period_start": fields.date.today() - relativedelta(years=1),
                "care_manager": self.care_manager.id,
            }
        )
        encounter.update({"episode_ids": [(4, ep2.id)]})
        self.assertEqual(encounter.period_start, ep1.period_start)

        ep0 = episode.create(
            {
                "encounter_id": encounter.id,
                "period_start": fields.date.today() - relativedelta(years=3),
                "care_manager": self.care_manager.id,
            }
        )
        encounter.update({"episode_ids": [(4, ep0.id)]})
        self.assertEqual(encounter.period_start, ep0.period_start)

        ep0.update({"period_start": fields.date.today() - relativedelta(years=4)})
        self.assertEqual(encounter.period_start, ep0.period_start)

    def test_flow(self):
        encounter = self.env["ni.encounter"].with_user(self.patient_admin)
        encounter = encounter.create({"patient_id": self.miss_glenda})
        episode = self.env["ni.care.episode"].with_user(self.patient_admin)

        self.assertEqual(encounter.state, "draft")
        with self.assertRaises(UserError):
            encounter.action_confirm()

        ep1 = episode.create(
            {
                "encounter_id": encounter.id,
                "period_start": fields.Date.add(fields.date.today(), months=1),
                "care_manager": self.care_manager,
            }
        )
        encounter.update({"episode_ids": [(4, ep1.id)]})
        encounter.action_confirm()

        self.assertEqual(encounter.state, "planned")

        encounter.state = "draft"
        ep1.update({"period_start": fields.date.today()})
        encounter.action_confirm()

        self.assertEqual(encounter.state, "in-progress")

        encounter.action_close()

        self.assertEqual(encounter.state, "finished")
