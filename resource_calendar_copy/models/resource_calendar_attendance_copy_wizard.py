#  Copyright (c) 2024 NSTDA
from odoo import fields, models


class AttendanceCopyWizard(models.TransientModel):
    _name = "resource.calendar.attendance.copy.wizard"
    _description = "Copy Working Hours Attendance"

    calendar_id = fields.Many2one("resource.calendar", required=True)
    dayofweek_filter = fields.Selection(
        [
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        "Day of Week",
        index=True,
    )
    attendance_ids = fields.Many2many(
        "resource.calendar.attendance",
        "resource_calendar_attendance_copy_wizard_rel",
        required=True,
        domain="[('calendar_id', '=?', calendar_id), ('dayofweek', '=?', dayofweek_filter)]",
    )

    dayofweek = fields.Selection(
        [
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        "Day of Week",
        required=True,
        default="0",
    )

    def action_copy(self):
        self.attendance_ids.action_copy_other_day([self.dayofweek])
