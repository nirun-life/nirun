#  Copyright (c) 2025 NSTDA

from odoo.exceptions import ValidationError
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
