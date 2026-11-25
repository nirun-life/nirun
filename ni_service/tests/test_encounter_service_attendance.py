#  Copyright (c) 2024 NSTDA

from odoo import fields
from odoo.tests import tagged

from .common import TestServiceCommon


@tagged("-at_install", "post_install")
class TestFindMatchingRequest(TestServiceCommon):
    """Tests for _find_matching_request auto-mapping logic."""

    def _new_attendance(self, **overrides):
        vals = {
            "encounter_id": self.encounter.id,
            "attendance_id": self.attendance_slot.id,
            "service_id": self.service.id,
            "service_ids": [(4, self.service.id)],
        }
        vals.update(overrides)
        return self.env["ni.encounter.service.attendance"].new(vals)

    # --- matching logic ---

    def test_match_within_period(self):
        attendance = self._new_attendance()
        result = attendance._find_matching_request()
        self.assertEqual(result, self.service_request)

    def test_no_match_different_service(self):
        other = self.env["ni.service"].create(
            {
                "name": "Occupational Therapy",
                "company_id": self.env.company.id,
                "category_id": self.category.id,
            }
        )
        attendance = self._new_attendance(
            service_id=other.id,
            service_ids=[(4, other.id)],
        )
        self.assertFalse(attendance._find_matching_request())

    def test_no_match_different_patient(self):
        partner2 = self.env["res.partner"].create({"name": "Another Patient"})
        other_patient = self.env["ni.patient"].create(
            {
                "partner_id": partner2.id,
                "company_id": self.env.company.id,
            }
        )
        enc_class = self.env.ref("ni_patient.class_AMB")
        other_encounter = self.env["ni.encounter"].create(
            {
                "patient_id": other_patient.id,
                "class_id": enc_class.id,
                "period_start": fields.Datetime.from_string("2027-01-04 08:00:00"),
                "identifier": "TEST-ENC-OTHER",
            }
        )
        attendance = self._new_attendance(encounter_id=other_encounter.id)
        self.assertFalse(attendance._find_matching_request())

    def test_no_match_before_period_start(self):
        # Request starts 2027-01-04; encounter is in Dec 2026 → no match
        early_enc = self._make_encounter("2026-12-01 08:00:00", "TEST-ENC-EARLY")
        attendance = self._new_attendance(encounter_id=early_enc.id)
        self.assertFalse(attendance._find_matching_request())

    def test_no_match_after_period_end(self):
        # Request ends 2027-03-31; encounter is Apr 2027 → no match
        late_enc = self._make_encounter("2027-04-01 08:00:00", "TEST-ENC-LATE")
        attendance = self._new_attendance(encounter_id=late_enc.id)
        self.assertFalse(attendance._find_matching_request())

    def test_open_ended_period_matches_future_encounter(self):
        self.service_request.period_end = False
        future_enc = self._make_encounter("2028-06-01 08:00:00", "TEST-ENC-FUTURE")
        attendance = self._new_attendance(encounter_id=future_enc.id)
        self.assertEqual(attendance._find_matching_request(), self.service_request)

    def test_matches_via_service_ids_not_only_service_id(self):
        second_service = self.env["ni.service"].create(
            {
                "name": "Hydrotherapy",
                "company_id": self.env.company.id,
                "category_id": self.category.id,
            }
        )
        self.service_request.service_ids = [(4, second_service.id)]
        attendance = self._new_attendance(
            service_id=second_service.id,
            service_ids=[(4, second_service.id)],
        )
        self.assertEqual(attendance._find_matching_request(), self.service_request)

    # --- create() integration ---

    def test_auto_fill_request_id_on_create(self):
        attendance = self.env["ni.encounter.service.attendance"].create(
            {
                "encounter_id": self.encounter.id,
                "attendance_id": self.attendance_slot.id,
                "service_id": self.service.id,
                "service_ids": [(4, self.service.id)],
            }
        )
        self.assertEqual(attendance.request_id, self.service_request)

    def test_create_takes_the_first_service(self):
        attendance = self.env["ni.encounter.service.attendance"].create(
            {
                "encounter_id": self.encounter.id,
                "attendance_id": self.attendance_slot.id,
                "service_ids": [(4, self.service.id)],
            }
        )
        self.assertEqual(attendance.service_id, self.service)
        self.assertEqual(attendance.request_id, self.service_request)

    def test_existing_request_id_not_overridden_on_create(self):
        other_request = self.env["ni.service.request"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "name": "Other Program",
                "service_ids": [(4, self.service.id)],
                "period_start": fields.Datetime.from_string("2027-01-04 08:00:00"),
                "period_end": fields.Datetime.from_string("2027-03-31 23:59:59"),
            }
        )
        attendance = self.env["ni.encounter.service.attendance"].create(
            {
                "encounter_id": self.encounter.id,
                "attendance_id": self.attendance_slot.id,
                "service_id": self.service.id,
                "service_ids": [(4, self.service.id)],
                "request_id": other_request.id,
            }
        )
        self.assertEqual(attendance.request_id, other_request)

    def test_multi_service_partial_overlap_matches(self):
        # Request has [physio, hydro], attendance has [hydro, occupational]
        # Shared: hydro → should match
        hydro = self.env["ni.service"].create(
            {
                "name": "Hydrotherapy",
                "company_id": self.env.company.id,
                "category_id": self.category.id,
            }
        )
        occupational = self.env["ni.service"].create(
            {
                "name": "Occupational Therapy",
                "company_id": self.env.company.id,
                "category_id": self.category.id,
            }
        )
        self.service_request.service_ids = [(4, hydro.id)]  # now [physio, hydro]
        attendance = self._new_attendance(
            service_id=hydro.id,
            service_ids=[(6, 0, [hydro.id, occupational.id])],
        )
        self.assertEqual(attendance._find_matching_request(), self.service_request)

    def test_multi_service_no_overlap_no_match(self):
        # Request has [physio, hydro], attendance has [occupational, speech]
        # No overlap → should not match
        hydro = self.env["ni.service"].create(
            {
                "name": "Hydrotherapy",
                "company_id": self.env.company.id,
                "category_id": self.category.id,
            }
        )
        occupational = self.env["ni.service"].create(
            {
                "name": "Occupational Therapy",
                "company_id": self.env.company.id,
                "category_id": self.category.id,
            }
        )
        speech = self.env["ni.service"].create(
            {
                "name": "Speech Therapy",
                "company_id": self.env.company.id,
                "category_id": self.category.id,
            }
        )
        self.service_request.service_ids = [(4, hydro.id)]  # now [physio, hydro]
        attendance = self._new_attendance(
            service_id=occupational.id,
            service_ids=[(6, 0, [occupational.id, speech.id])],
        )
        self.assertFalse(attendance._find_matching_request())

    def test_no_request_id_when_no_matching_request(self):
        other_service = self.env["ni.service"].create(
            {
                "name": "No Request Service",
                "company_id": self.env.company.id,
                "category_id": self.category.id,
            }
        )
        attendance = self.env["ni.encounter.service.attendance"].create(
            {
                "encounter_id": self.encounter.id,
                "attendance_id": self.attendance_slot.id,
                "service_id": other_service.id,
                "service_ids": [(4, other_service.id)],
            }
        )
        self.assertFalse(attendance.request_id)


@tagged("-at_install", "post_install")
class TestGenerateService(TestServiceCommon):
    def setUp(self):
        super().setUp()
        self.service.write(
            {
                "calendar_id": self.calendar.id,
                "attendance_ids": [(4, self.attendance_slot.id)],
            }
        )
        self.encounter.resource_calendar_id = self.calendar

    def _create_event(self, day="2027-01-04", **vals):
        return self.env["ni.service.event"].create(
            {
                "service_id": self.service.id,
                "service_ids": [(4, self.service.id)],
                "calendar_id": self.calendar.id,
                "attendance_ids": [(4, self.attendance_slot.id)],
                "start": f"{day} 01:00:00",
                "stop": f"{day} 05:00:00",
                **vals,
            }
        )

    def _generate(self):
        self.encounter.action_generate_service_resource()
        return self.encounter.service_attendance_ids

    def test_generate_without_event(self):
        line = self._generate()
        self.assertEqual(line.service_id, self.service)
        self.assertEqual(line.attendance_id, self.attendance_slot)
        self.assertFalse(line.service_event_id)

    def test_generate_prefers_the_planned_event(self):
        event = self._create_event()
        planned = self._create_event(plan_patient_ids=[(4, self.patient.id)])
        self._create_event("2027-01-11", plan_patient_ids=[(4, self.patient.id)])
        self.assertEqual(self._generate().service_event_id, planned)
        planned.plan_patient_ids = False
        planned.unlink()
        self.assertEqual(self._generate().service_event_id, event)

    def test_generate_takes_the_day_of_the_user(self):
        # Monday 06:30 in Bangkok, Sunday in UTC
        event = self._create_event()
        self.encounter.period_start = "2027-01-03 23:30:00"
        line = self._generate()
        self.assertEqual(line.dayofweek, "0")
        self.assertEqual(line.service_event_id, event)

    def test_generate_user_without_timezone(self):
        event = self._create_event()
        self.env.user.tz = False
        line = self._generate()
        self.assertEqual(line.dayofweek, "0")
        self.assertEqual(line.service_event_id, event)

    def test_day_of_week_without_encounter(self):
        self.assertFalse(self.env["ni.encounter.service.attendance"].new().dayofweek)
