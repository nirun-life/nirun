#  Copyright (c) 2025 NSTDA

from odoo.tests import TransactionCase


class TestHrAttendanceMyArea(TransactionCase):
    def test_action_domain_scoped_to_my_area(self):
        action = self.env.ref("hr_attendance.hr_attendance_action")
        self.assertIn("employee_id.my_area", action.domain)

    def test_action_overview_domain_scoped_to_my_area(self):
        action = self.env.ref("hr_attendance.hr_attendance_action_overview")
        self.assertIn("employee_id.my_area", action.domain)

    def test_action_overview_view_mode_includes_kanban_and_form(self):
        action = self.env.ref("hr_attendance.hr_attendance_action_overview")
        view_modes = action.view_mode.split(",")
        self.assertIn("kanban", view_modes)
        self.assertIn("form", view_modes)

    def test_my_area_filter_in_search_view(self):
        view = self.env.ref(
            "ni_community_care_attendance.hr_attendance_view_filter_inherit"
        )
        self.assertIn("my_area_employees", view.arch)
        self.assertIn("employee_id.my_area", view.arch)
