# HR Employee Attendance Report View (`hr_attendance_report_view`)

## Purpose

Extends Odoo attendance reporting with richer attendance-report dimensions and a separate SQL-backed report for employees who
have no daily check-in records.

## Main Components

- `hr.attendance.report` extension Changes the default ordering to `check_in desc, employee_id`, uses `employee_id` as the
  record name, and adds readonly `state_id` and `job_id` dimensions. It also overrides `_select()` so those fields and
  `overtime_hours` are available in the report query.
- `hr.attendance.missing.report` New `_auto = False` SQL view model listing employee/day combinations without a matching
  attendance check-in.

## Views and Security

- Reconfigures the base attendance report action to open in `pivot,tree,graph` mode with day and employee grouping by default.
- Attendance report views: sets the default period filter to `this_month`, adds custom tree, pivot, and form views, and exposes
  overtime as an optional measure.
- Missing-attendance report views: provides search and tree views with date, department, job, and company grouping.
- Security: grants read-only access to `hr.attendance.missing.report` and applies a multi-company rule on `company_id`.

## Dependencies

- `hr_attendance`
- `ni_community_care`

## Notes

- The missing-attendance SQL view builds a full date series from the minimum to maximum `hr_attendance.check_in` date, then
  cross joins that range with every employee before excluding days that have a localized check-in.
- Missing-check detection uses each employee's resource calendar timezone when deriving the attendance date.
