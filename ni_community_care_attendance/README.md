# Community Care - Attendance (`ni_community_care_attendance`)

Odoo 16.0 module that links community-care operations with attendance, leave, and workforce summary views.

## Purpose

`ni_community_care_attendance` extends community-care staffing workflows with attendance-aware dashboards, leave constraints,
and approval-period attendance summaries so field teams can compare service work with actual staff presence.

## Main Models

| Model                       | Role                                                      |
| --------------------------- | --------------------------------------------------------- |
| `hr.employee`               | Extended with attendance and leave summary metrics        |
| `hr.attendance`             | Extended with additional write-time validation behavior   |
| `hr.leave`                  | Extended leave behavior for allocation handling           |
| `ni.service.event.approval` | Extended with attendance aggregation for approval windows |
| `ni.employee.report`        | Employee dashboard helper                                 |
| `hr.leave.report`           | Extended leave analysis entry point                       |

## Behavior and UI

- `models/hr_employee.py` computes whether staff attended today, days attended this month, care days this month, and whether
  they are currently on leave.
- `models/ni_service_event_approval.py` adds linked attendance records plus aggregate attendance days and hours for approval
  periods.
- `models/hr_leave.py` and `models/hr_attendance.py` refine leave and attendance behavior for this deployment.
- `views/hr_employee_views.xml`, `views/hr_leave_views.xml`, `views/hr_attendance_views.xml`, and
  `views/ni_service_event_approval_views.xml` expose the staffing and approval-side additions.
- Frontend assets under `static/src/components/*` and `static/src/views/*` add attendance-specific dashboards and list headers.

## Security and Dependencies

- `security/ir_rules_data.xml` adds record-rule behavior for the attendance layer.
- The module depends on `ni_community_care` and `hr_holidays_attendance`.

## Verification

- Re-check approval-period attendance summaries after changes to date-range or timezone logic.
- Review employee dashboard values for attendance days, care days, and leave status.
- The module includes `tests/test_hr_attendance_my_area.py` for area-aware attendance behavior.
