#  Copyright (c) 2025 NSTDA
from odoo import fields, models


class HrAttendanceReport(models.Model):
    _inherit = "hr.attendance.report"
    _order = "check_in desc, employee_id"
    _rec_name = "employee_id"

    employee_id = fields.Many2one(group_operator="count_distinct")
