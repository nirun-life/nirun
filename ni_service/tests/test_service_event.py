#  Copyright (c) 2026 NSTDA

from freezegun import freeze_time

from odoo import fields
from odoo.tests import Form, tagged

from .common import TestServiceCommon

EVENT_START = "2027-01-04 08:00:00"
EVENT_STOP = "2027-01-04 09:00:00"


@tagged("-at_install", "post_install")
class TestServiceEvent(TestServiceCommon):
    @freeze_time(EVENT_START)
    def test_create_service_event(self):
        event = self.env["ni.service.event"].create(
            {
                "service_id": self.service.id,
                "service_ids": [(4, self.service.id)],
                "start": fields.Datetime.from_string(EVENT_START),
                "stop": fields.Datetime.from_string(EVENT_STOP),
            }
        )

        self.assertTrue(event.event_id)
        self.assertEqual(event.name, self.service.name)
        self.assertEqual(event.service_category_ids, self.category)

    def test_create_from_patient_form_adds_no_activity_on_patient(self):
        event = (
            self.env["ni.service.event"]
            .with_context(active_model="ni.patient", active_id=self.patient.id)
            .create(
                {
                    "service_id": self.service.id,
                    "service_ids": [(4, self.service.id)],
                    "start": fields.Datetime.from_string(EVENT_START),
                    "stop": fields.Datetime.from_string(EVENT_STOP),
                }
            )
        )

        self.assertFalse(event.res_model)
        self.assertFalse(self.patient.activity_ids)

    def _create_event(self, **vals):
        return self.env["ni.service.event"].create(
            {
                "service_id": self.service.id,
                "service_ids": [(4, self.service.id)],
                "start": EVENT_START,
                "stop": EVENT_STOP,
                **vals,
            }
        )

    def test_day_of_week_is_the_day_of_the_user(self):
        # Monday 06:00 in Bangkok
        event = self._create_event(
            start="2027-01-03 23:00:00", stop="2027-01-04 00:00:00"
        )
        self.assertEqual(event.dayofweek, "0")
        event.start = "2027-01-02 23:00:00"
        self.assertEqual(event.dayofweek, "6")

    def test_onchange_attendance_keeps_the_day_of_the_user(self):
        event = self._create_event(
            start="2027-01-03 23:00:00",
            stop="2027-01-04 00:00:00",
            event_tz="Asia/Bangkok",
            calendar_id=self.calendar.id,
            attendance_ids=[(4, self.attendance_slot.id)],
        )
        event._onchange_attendance_id()
        self.assertEqual(event.attendance_ids, self.attendance_slot)
        self.assertEqual(str(event.start), "2027-01-04 01:00:00")
        self.assertEqual(str(event.stop), "2027-01-04 05:00:00")

    def test_float_time_to_datetime(self):
        convert = self.env["ni.service.event"].float_time_to_datetime
        date = fields.Date.to_date("2027-01-04")
        for hour, expected in (
            (0.0, "2027-01-03 17:00:00"),
            (8.35, "2027-01-04 01:21:00"),
            (24.0, "2027-01-04 17:00:00"),
        ):
            self.assertEqual(str(convert(date, hour, "Asia/Bangkok")), expected)
        self.assertFalse(convert(date, False))

    def test_user_without_timezone(self):
        self.service_user.tz = False
        event = self._create_event().with_user(self.service_user)
        self.assertEqual(event.dayofweek, "0")
        date = fields.Date.to_date("2027-01-04")
        self.assertEqual(
            str(event.float_time_to_datetime(date, 8.0)), "2027-01-04 08:00:00"
        )

    def test_event_is_a_calendar_event(self):
        event = self._create_event(name="Ignored")
        meeting = event.event_id
        self.assertEqual(meeting.name, self.service.name)
        self.assertEqual(meeting.start, event.start)
        self.assertEqual(event.duration, 1.0)

        # moved in the service calendar, then in the personal calendar
        event.write({"start": "2027-01-05 08:00:00", "stop": "2027-01-05 10:00:00"})
        self.assertEqual(str(meeting.start), "2027-01-05 08:00:00")
        self.assertEqual(meeting.duration, 2.0)
        meeting.write({"start": "2027-01-06 08:00:00", "stop": "2027-01-06 09:00:00"})
        self.assertEqual(str(event.start), "2027-01-06 08:00:00")
        self.assertEqual(event.duration, 1.0)
        self.assertEqual(event.dayofweek, "2")

        meeting.unlink()
        self.assertFalse(event.exists())

    def test_form(self):
        self.service.employee_ids = self.env["hr.employee"].create(
            {"name": "Therapist", "user_id": self.service_manager.id}
        )
        form = Form(self.env["ni.service.event"].with_user(self.service_user))
        form.service_ids.add(self.service)
        form.start = "2027-01-04 02:00:00"
        form.stop = "2027-01-04 03:00:00"
        event = form.save()
        self.assertEqual(event.service_id, self.service)
        self.assertEqual(event.mode, "single")
        self.assertEqual(event.user_id, self.service_user)
        self.assertIn(self.service_manager.partner_id, event.partner_ids)
        self.assertEqual(event.service_category_id, self.category)
