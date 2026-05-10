#  Copyright (c) 2024 NSTDA

from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError

from .common import TestServiceEventCommon


class TestOnchangeServiceId(TestServiceEventCommon):
    """Selecting a service must not override the caregiver (user_id)."""

    def test_user_id_not_overridden_by_service(self):
        # Base onchange would set user_id = service.employee_id.user_id (other_user).
        # The override must restore it to the original value.
        original_user = self.event.user_id
        self.event._onchange_service_id()
        self.assertEqual(self.event.user_id, original_user)

    def test_user_id_not_changed_to_service_employee_user(self):
        self.event._onchange_service_id()
        self.assertNotEqual(self.event.user_id, self.other_user)


class TestCheckStartDate(TestServiceEventCommon):
    def test_today_start_is_allowed(self):
        event = self._make_event(start=fields.Datetime.now())
        self.assertTrue(event.id)

    def test_within_backdate_limit_is_allowed(self):
        within = fields.Datetime.now() - timedelta(days=3)
        event = self._make_event(start=within)
        self.assertTrue(event.id)

    def test_future_start_raises(self):
        tomorrow = fields.Datetime.now() + timedelta(days=1)
        with self.assertRaises(UserError):
            self._make_event(start=tomorrow)

    def test_beyond_backdate_limit_raises(self):
        # default backdate_limit_days = 7
        too_old = fields.Datetime.now() - timedelta(days=8)
        with self.assertRaises(UserError):
            self._make_event(start=too_old)

    def test_custom_limit_allows_older_date(self):
        self.env.company.backdate_limit_days = 30
        twenty_days_ago = fields.Datetime.now() - timedelta(days=20)
        event = self._make_event(start=twenty_days_ago)
        self.assertTrue(event.id)

    def test_unlimited_mode_before_system_start_raises(self):
        self.env.company.backdate_limit_days = -1
        self.env.company.system_start_date = fields.Date.today() - timedelta(days=10)
        before_system_start = fields.Datetime.now() - timedelta(days=15)
        with self.assertRaises(UserError):
            self._make_event(start=before_system_start)

    def test_unlimited_mode_after_system_start_is_allowed(self):
        self.env.company.backdate_limit_days = -1
        self.env.company.system_start_date = fields.Date.today() - timedelta(days=30)
        within_range = fields.Datetime.now() - timedelta(days=15)
        event = self._make_event(start=within_range)
        self.assertTrue(event.id)

    def test_unlimited_mode_without_system_start_any_past_date_allowed(self):
        self.env.company.backdate_limit_days = -1
        self.env.company.system_start_date = False
        very_old = fields.Datetime.now() - timedelta(days=365)
        event = self._make_event(start=very_old)
        self.assertTrue(event.id)


class TestCheckEmployeeId(TestServiceEventCommon):
    def test_employee_set_from_user_employee_link(self):
        event = self._make_event(user=self.other_user)
        self.assertEqual(event.employee_id, self.employee)

    def test_no_employee_when_user_has_no_linked_employee(self):
        bare_user = self.env["res.users"].create(
            {
                "name": "Bare User",
                "login": "bare@test.com",
                "groups_id": [(4, self.env.ref("base.group_user").id)],
            }
        )
        event = self._make_event(user=bare_user)
        self.assertFalse(event.employee_id)


class TestComputeMyServiceEvent(TestServiceEventCommon):
    def test_true_when_event_belongs_to_current_user(self):
        # Default event has user_id = admin (env.user).
        self.event._compute_my_service_event()
        self.assertTrue(self.event.my_service_event)

    def test_false_when_event_belongs_to_other_user(self):
        # Create an event owned by other_user; env.user (admin) != other_user → False.
        event = self._make_event(user=self.other_user)
        event._compute_my_service_event()
        self.assertFalse(event.my_service_event)


class TestSearchMyServiceEvent(TestServiceEventCommon):
    def test_true_operand_returns_equal_domain(self):
        domain = self.event._search_my_service_event("=", True)
        self.assertEqual(domain, [("user_id", "=", self.env.user.id)])

    def test_false_operand_returns_not_equal_domain(self):
        domain = self.event._search_my_service_event("=", False)
        self.assertEqual(domain, [("user_id", "!=", self.env.user.id)])

    def test_unsupported_operator_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            self.event._search_my_service_event("!=", True)


class TestComputeStateCity(TestServiceEventCommon):
    def test_state_and_city_empty_when_no_plan_patients(self):
        self.event.plan_patient_ids = [(5, 0, 0)]
        self.event._compute_state_city()
        self.assertFalse(self.event.state_id)
        self.assertFalse(self.event.city_id)
