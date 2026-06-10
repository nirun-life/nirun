# Buddhist Calendar (`l10n_th_web_buddhist_calendar`)

## Purpose

Converts Thai date and datetime presentation from Gregorian years to Buddhist Era (B.E.) across web widgets, grouped list
labels, QWeb formatting, mail rendering, and mail tracking output.

## Main Components

- Backend assets Replaces Odoo's bundled `jquery-ui.js` and `tempusdominus.js`, and loads custom date/calendar widget patches
  for calendar, list, kanban, date, and datetime views.
- QWeb converters Extends `ir.qweb.field.date` and `ir.qweb.field.datetime` to add 543 years for `th_TH`.
- Mail rendering and tracking patches Overrides mail template date formatting helpers and mail-tracking display values for Thai
  locale output.
- Read-group patch Replaces `BaseModel._read_group_format_result` globally so grouped date labels show B.E. years for `th_TH`.

## Dependencies

- `web`
- `mail`

## Notes

- This module uses global monkey patches on core Odoo classes and mail helpers, so its behavior applies repo-wide once
  installed.
- The year conversion is presentation-focused. Stored dates remain Gregorian.
