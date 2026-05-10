#  Copyright (c) 2025 NSTDA

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests import TransactionCase


class MyAreaMixinCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        country = cls.env.ref("base.th")

        cls.state = cls.env["res.country.state"].create(
            {"name": "Test State A", "code": "TSA", "country_id": country.id}
        )
        cls.other_state = cls.env["res.country.state"].create(
            {"name": "Test State B", "code": "TSB", "country_id": country.id}
        )
        cls.city = cls.env["res.city"].create(
            {"name": "Test City A", "state_id": cls.state.id, "country_id": country.id}
        )
        cls.other_city = cls.env["res.city"].create(
            {
                "name": "Test City B",
                "state_id": cls.other_state.id,
                "country_id": country.id,
            }
        )

        cls.admin_user = cls.env["res.users"].create(
            {
                "name": "Test Admin",
                "login": "mixin_admin@test.com",
                "groups_id": [(4, cls.env.ref("ni_patient.group_admin").id)],
            }
        )
        cls.manager_user = cls.env["res.users"].create(
            {
                "name": "Test Manager",
                "login": "mixin_manager@test.com",
                "groups_id": [(4, cls.env.ref("ni_patient.group_manager").id)],
                "state_ids": [(4, cls.state.id)],
            }
        )
        cls.regular_user = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "mixin_user@test.com",
                "groups_id": [(4, cls.env.ref("ni_patient.group_user").id)],
                "city_ids": [(4, cls.city.id)],
            }
        )

        cls.employee_in = cls.env["hr.employee"].create(
            {
                "name": "Employee In Area",
                "state_ids": [(4, cls.state.id)],
                "city_ids": [(4, cls.city.id)],
            }
        )
        cls.employee_out = cls.env["hr.employee"].create(
            {
                "name": "Employee Out Of Area",
                "state_ids": [(4, cls.other_state.id)],
                "city_ids": [(4, cls.other_city.id)],
            }
        )


class TestComputeMyAreaEmployee(MyAreaMixinCommon):
    """_compute_my_area on hr.employee (city_ids / state_ids M2M path)."""

    def test_admin_always_true_regardless_of_city(self):
        self.assertTrue(self.employee_out.with_user(self.admin_user).my_area)

    def test_admin_always_true_in_area(self):
        self.assertTrue(self.employee_in.with_user(self.admin_user).my_area)

    def test_manager_true_when_state_matches(self):
        self.assertTrue(self.employee_in.with_user(self.manager_user).my_area)

    def test_manager_false_when_state_no_match(self):
        self.assertFalse(self.employee_out.with_user(self.manager_user).my_area)

    def test_user_true_when_city_matches(self):
        self.assertTrue(self.employee_in.with_user(self.regular_user).my_area)

    def test_user_false_when_city_no_match(self):
        self.assertFalse(self.employee_out.with_user(self.regular_user).my_area)


class TestComputeMyAreaUser(MyAreaMixinCommon):
    """_compute_my_area on res.users (city_ids / state_ids M2M path)."""

    def test_admin_always_true(self):
        self.assertTrue(self.regular_user.with_user(self.admin_user).my_area)

    def test_manager_true_when_state_matches(self):
        # manager_user's state_ids = [cls.state]; regular_user has no state → False
        # Use manager_user itself as the record (it has state_ids = [cls.state])
        self.assertTrue(self.manager_user.with_user(self.manager_user).my_area)

    def test_user_true_when_city_matches(self):
        self.assertTrue(self.regular_user.with_user(self.regular_user).my_area)

    def test_user_false_when_city_no_match(self):
        self.assertFalse(self.manager_user.with_user(self.regular_user).my_area)


class TestSearchMyAreaEmployee(MyAreaMixinCommon):
    """_search_my_area domain output on hr.employee (city_ids / state_ids path)."""

    def _search(self, user, operand):
        return self.env["hr.employee"].with_user(user)._search_my_area("=", operand)

    def test_admin_true_returns_empty_domain(self):
        self.assertEqual(self._search(self.admin_user, True), [])

    def test_admin_false_returns_no_records_domain(self):
        self.assertEqual(self._search(self.admin_user, False), [("id", "=", 0)])

    def test_manager_true_filters_by_state_ids(self):
        domain = self._search(self.manager_user, True)
        self.assertEqual(domain, [("state_ids", "in", self.manager_user.state_ids.ids)])

    def test_manager_false_excludes_state_ids(self):
        domain = self._search(self.manager_user, False)
        self.assertEqual(
            domain, [("state_ids", "not in", self.manager_user.state_ids.ids)]
        )

    def test_user_true_filters_by_city_ids(self):
        domain = self._search(self.regular_user, True)
        self.assertEqual(domain, [("city_ids", "in", self.regular_user.city_ids.ids)])

    def test_user_false_excludes_city_ids(self):
        domain = self._search(self.regular_user, False)
        self.assertEqual(
            domain, [("city_ids", "not in", self.regular_user.city_ids.ids)]
        )

    def test_unsupported_operator_raises(self):
        with self.assertRaises(ValidationError):
            self._search(self.regular_user, True)
            self.env["hr.employee"].with_user(self.regular_user)._search_my_area(
                "!=", True
            )


class TestSearchMyAreaReport(MyAreaMixinCommon):
    """_search_my_area domain output on ni.service.event.report (city_id / state_id path).

    Report models are SQL views — no records are created; only the domain logic is
    verified by calling the search method directly.
    """

    def _search(self, user, operand):
        return (
            self.env["ni.service.event.report"]
            .with_user(user)
            ._search_my_area("=", operand)
        )

    def test_admin_true_returns_empty_domain(self):
        self.assertEqual(self._search(self.admin_user, True), [])

    def test_manager_true_filters_by_state_id(self):
        domain = self._search(self.manager_user, True)
        self.assertEqual(domain, [("state_id", "in", self.manager_user.state_ids.ids)])

    def test_manager_false_excludes_state_id(self):
        domain = self._search(self.manager_user, False)
        self.assertEqual(
            domain, [("state_id", "not in", self.manager_user.state_ids.ids)]
        )

    def test_user_true_filters_by_city_id(self):
        domain = self._search(self.regular_user, True)
        self.assertEqual(domain, [("city_id", "in", self.regular_user.city_ids.ids)])

    def test_user_false_excludes_city_id(self):
        domain = self._search(self.regular_user, False)
        self.assertEqual(
            domain, [("city_id", "not in", self.regular_user.city_ids.ids)]
        )

    def test_unsupported_operator_raises(self):
        with self.assertRaises(ValidationError):
            self.env["ni.service.event.report"].with_user(
                self.regular_user
            )._search_my_area("!=", True)


class TestComputeMyAreaReport(MyAreaMixinCommon):
    """_compute_my_area on ni.service.event.report / ni.service.event.daily.report
    (city_id / state_id singular path).

    Creates a complete service event stack so the SQL views have records.
    Note: _compute_state_city on ni.service.event has a bugged @api.depends
    (lists state_id/city_id instead of plan_patient_ids), so we call it manually
    after event creation to populate the stored city/state from the patient.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.patient_type = cls.env["ni.patient.type"].create(
            {"name": "Test Report Type"}
        )
        cls.category = cls.env["ni.service.category"].create(
            {"name": "Test Report Category"}
        )
        cls.service = cls.env["ni.service"].create(
            {
                "name": "Test Report Service",
                "category_id": cls.category.id,
                "dayofweek": "0",
            }
        )

        def make_patient(name, city, state):
            patient = cls.env["ni.patient"].create({"name": name})
            patient.partner_id.write({"city_id": city.id, "state_id": state.id})
            return patient

        cls.patient_in = make_patient("Patient In Area", cls.city, cls.state)
        cls.patient_out = make_patient(
            "Patient Out Area", cls.other_city, cls.other_state
        )

        def make_event(patient):
            now = fields.Datetime.now()
            event = cls.env["ni.service.event"].create(
                {
                    "name": "Test Report Event",
                    "start": now,
                    "stop": now + timedelta(hours=1),
                    "service_id": cls.service.id,
                    "service_ids": [Command.set([cls.service.id])],
                    "patient_type_id": cls.patient_type.id,
                    "service_category_id": cls.category.id,
                    "plan_patient_ids": [Command.link(patient.id)],
                }
            )
            event._compute_state_city()
            return event

        cls.event_in = make_event(cls.patient_in)
        cls.event_out = make_event(cls.patient_out)

        cls.report_in = cls.env["ni.service.event.report"].search(
            [("event_id", "=", cls.event_in.id)], limit=1
        )
        cls.report_out = cls.env["ni.service.event.report"].search(
            [("event_id", "=", cls.event_out.id)], limit=1
        )
        cls.daily_in = cls.env["ni.service.event.daily.report"].search(
            [("employee_id", "=", cls.event_in.employee_id.id)], limit=1
        )

    def test_report_records_exist(self):
        self.assertTrue(
            self.report_in, "report_in record missing — check SQL view setup"
        )
        self.assertTrue(
            self.report_out, "report_out record missing — check SQL view setup"
        )

    def test_admin_always_true(self):
        self.assertTrue(self.report_in.with_user(self.admin_user).my_area)

    def test_manager_true_when_state_matches(self):
        self.assertTrue(self.report_in.with_user(self.manager_user).my_area)

    def test_manager_false_when_state_no_match(self):
        self.assertFalse(self.report_out.with_user(self.manager_user).my_area)

    def test_user_true_when_city_matches(self):
        self.assertTrue(self.report_in.with_user(self.regular_user).my_area)

    def test_user_false_when_city_no_match(self):
        self.assertFalse(self.report_out.with_user(self.regular_user).my_area)
