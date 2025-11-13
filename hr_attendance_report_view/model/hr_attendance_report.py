#  Copyright (c) 2025 NSTDA
from odoo import api, fields, models


class HrAttendanceReport(models.Model):
    _inherit = "hr.attendance.report"
    _order = "check_in desc, employee_id"
    _rec_name = "employee_id"

    employee_id = fields.Many2one(group_operator="count_distinct")

    state_id = fields.Many2one("res.country.state", "จังหวัด", readonly=True)
    job_id = fields.Many2one("hr.job", "ตำแหน่งงาน", readonly=True, index=True)

    @api.model
    def _select(self):
        return """
              SELECT
                  hra.id,
                  hr_employee.department_id,
                  hra.employee_id,
                  hr_employee.company_id,
                  hra.check_in,
                  hra.worked_hours,
                  coalesce(ot.duration, 0) as overtime_hours,
                  hr_employee.state_id,
                  hr_employee.job_id
          """
