# Resource Calendar Copy (`resource_calendar_copy`)

## Purpose

Adds a wizard for copying working-time attendance lines from one day of a resource calendar to another day.

## Main Components

- `resource.calendar` extension Adds `action_copy_wizard()` to open the copy dialog from a calendar.
- `resource.calendar.attendance` extension Adds day-label helpers and `action_copy_other_day()` for duplicating attendance lines
  to target weekdays.
- `resource.calendar.attendance.copy.wizard` Transient wizard that filters attendance lines by calendar and source weekday, then
  copies them to a selected target day.

## Views and Security

- Resource calendar form: adds a `Copy Attendance` header button.
- Wizard form: shows calendar, source day filter, source attendance lines, and target weekday.
- Security: grants full access to the wizard model for `base.group_system`.

## Dependencies

- `resource`

## Notes

- Copied lines update `name` by replacing any detected weekday label, or by appending `({dow})` when no label is found.
