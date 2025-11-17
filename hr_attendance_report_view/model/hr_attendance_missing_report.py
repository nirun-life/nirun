#  Copyright (c) 2025 NSTDA
from odoo import fields, models, tools


class HrAttendanceMissingReport(models.Model):
    _name = "hr.attendance.missing.report"
    _description = "Employees Missing Daily Check-in"
    _auto = False  # This is a SQL-based report

    employee_id = fields.Many2one("hr.employee", string="Employee", readonly=True)
    department_id = fields.Many2one("hr.department", string="Department", readonly=True)
    company_id = fields.Many2one("res.company", string="Company", readonly=True)
    job_id = fields.Many2one("hr.job", string="Job Position", readonly=True)
    country_id = fields.Many2one("res.country", string="Country", readonly=True)
    state_id = fields.Many2one("res.country.state", string="State", readonly=True)
    date = fields.Date(string="Date", readonly=True)
    active = fields.Boolean("Employee Active?", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW hr_attendance_missing_report AS
            WITH date_series AS (
                SELECT generate_series(
                    (SELECT MIN(check_in)::date FROM hr_attendance),
                    (SELECT MAX(check_in)::date FROM hr_attendance),
                    interval '1 day'
                )::date AS day
            ),
            employee_days AS (
                SELECT e.id AS employee_id, e.department_id, e.company_id, e.country_id, e.state_id, e.job_id, d.day, e.active
                FROM hr_employee e
                CROSS JOIN date_series d
            ),
            attendance_check AS (
                SELECT
                    employee_id,
                    ((check_in AT TIME ZONE 'utc') AT TIME ZONE (
                        SELECT calendar.tz
                        FROM resource_calendar calendar
                        JOIN hr_employee emp ON emp.id = hr_attendance.employee_id
                        WHERE calendar.id = emp.resource_calendar_id
                    ))::date AS check_in_date
                FROM hr_attendance
            )
            SELECT
                row_number() OVER (ORDER BY ed.employee_id, ed.day) AS id,
                ed.employee_id,
                ed.department_id,
                ed.company_id,
                ed.country_id,
                ed.state_id,
                ed.job_id,
                ed.day AS date,
                ed.active
            FROM employee_days ed
            LEFT JOIN attendance_check ac
              ON ed.employee_id = ac.employee_id AND ed.day = ac.check_in_date
            WHERE ac.check_in_date IS NULL;
        """
        )
