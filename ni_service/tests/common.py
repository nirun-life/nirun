#  Copyright (c) 2024 NSTDA

from odoo import fields
from odoo.tests import common

# Request period: 2027-01-04 → 2027-03-31 (future, avoids period_start_date default=today issue)
REQUEST_START = "2027-01-04 08:00:00"  # Monday
REQUEST_END = "2027-03-31 23:59:59"
ENCOUNTER_START = REQUEST_START  # encounter must be <= request period_start


class TestServiceCommon(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.env.user.tz = "Asia/Bangkok"
        self.service_user = self.env["res.users"].create(
            {
                "name": "Service User",
                "login": "service.user@example.com",
                "email": "service.user@example.com",
                "password": "service-user",  # pragma: allowlist secret
                "company_id": self.env.company.id,
                "company_ids": [(6, 0, [self.env.company.id])],
                "groups_id": [
                    (4, self.ref("base.group_user")),
                    (4, self.ref("ni_patient.group_user")),
                ],
            }
        )
        self.service_manager = self.env["res.users"].create(
            {
                "name": "Service Manager",
                "login": "service.manager@example.com",
                "email": "service.manager@example.com",
                "password": "service-manager",  # pragma: allowlist secret
                "company_id": self.env.company.id,
                "company_ids": [(6, 0, [self.env.company.id])],
                "groups_id": [
                    (4, self.ref("base.group_user")),
                    (4, self.ref("ni_patient.group_manager")),
                ],
            }
        )
        self.service_admin = self.env["res.users"].create(
            {
                "name": "Service Admin",
                "login": "service.admin@example.com",
                "email": "service.admin@example.com",
                "password": "service-admin",  # pragma: allowlist secret
                "company_id": self.env.company.id,
                "company_ids": [(6, 0, [self.env.company.id])],
                "groups_id": [
                    (4, self.ref("base.group_user")),
                    (4, self.ref("ni_patient.group_admin")),
                ],
            }
        )

        partner = self.env["res.partner"].create({"name": "Test Patient"})
        self.patient = self.env["ni.patient"].create(
            {
                "partner_id": partner.id,
                "company_id": self.env.company.id,
            }
        )

        self.calendar = self.env["resource.calendar"].create(
            {
                "name": "Test Calendar",
                "company_id": self.env.company.id,
                "attendance_ids": [(5,)],
            }
        )
        self.attendance_slot = self.env["resource.calendar.attendance"].create(
            {
                "name": "Morning",
                "calendar_id": self.calendar.id,
                "dayofweek": "0",
                "hour_from": 8.0,
                "hour_to": 12.0,
            }
        )

        enc_class = self.env.ref("ni_patient.class_AMB")
        self.encounter = self.env["ni.encounter"].create(
            {
                "patient_id": self.patient.id,
                "class_id": enc_class.id,
                "period_start": fields.Datetime.from_string(ENCOUNTER_START),
                "identifier": "TEST-ENC-001",
            }
        )

        self.category = self.env.ref("ni_service.categ_individual")
        self.service = self.env["ni.service"].create(
            {
                "name": "Physiotherapy",
                "company_id": self.env.company.id,
                "category_id": self.category.id,
            }
        )

        self.service_request = self.env["ni.service.request"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "name": "Physiotherapy Program",
                "service_ids": [(4, self.service.id)],
                "period_start": fields.Datetime.from_string(REQUEST_START),
                "period_end": fields.Datetime.from_string(REQUEST_END),
            }
        )

    def _make_encounter(self, period_start, identifier):
        enc_class = self.env.ref("ni_patient.class_AMB")
        return self.env["ni.encounter"].create(
            {
                "patient_id": self.patient.id,
                "class_id": enc_class.id,
                "period_start": fields.Datetime.from_string(period_start),
                "identifier": identifier,
            }
        )
