#  Copyright (c) 2026 NSTDA

from odoo.exceptions import UserError

from .common import TestPractitionerCommon


class TestHrEmployeeLicense(TestPractitionerCommon):
    def test_default_license_is_the_first_line_with_an_identifier(self):
        employee = self._create_employee("Doctor One")
        self._create_line(employee, "Some course")
        self.assertFalse(employee.license_default_id)
        line = self._create_line(employee, "Medical license", "M-0001")
        self.assertEqual(employee.license_default_id, line)
        self.assertEqual(employee.license_no, "Medical license")

    def test_selected_license_wins(self):
        other = self._create_line(self.performer, "Second license", "N-0002")
        self.performer.license_id = other
        self.assertEqual(self.performer.license_default_id, other)

    def test_category_cannot_be_its_own_ancestor(self):
        category = self.env["hr.employee.category"].create({"name": "Test parent"})
        child = self.env["hr.employee.category"].create(
            {"name": "Test child", "parent_id": category.id}
        )
        with self.assertRaises(UserError):
            category.parent_id = child
