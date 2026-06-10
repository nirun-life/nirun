# Service (`ni_service`)

Odoo 16.0 module that manages healthcare services, service requests, scheduled service events, and encounter attendance tracking
for Nirun. It ties service planning to calendars, encounter workflows, timing structures, and patient-facing summaries.

## Purpose

`ni_service` covers both the service catalog and the operational workflow around delivering services. It supports requested
services, scheduled calendar events, and encounter attendance records that can be matched back to the originating request.

## Main Models

| Model                             | Role                                                      |
| --------------------------------- | --------------------------------------------------------- |
| `ni.service`                      | Service catalog record                                    |
| `ni.service.category`             | Service category vocabulary                               |
| `ni.service.type`                 | Service type vocabulary                                   |
| `ni.service.request`              | Requested service workflow                                |
| `ni.service.event`                | Calendar-backed service delivery event                    |
| `ni.encounter.service.attendance` | Encounter attendance linked to a service event or request |

## Workflow, Data, and Views

- `ni.service.request` inherits request workflow, timing, identifier, and period behavior so planned services can be managed
  like other clinical requests.
- `ni.service.event` `_inherits` `calendar.event` and adds service-specific scheduling, patient planning, attachments, and
  encounter linkage.
- `datas/ir_sequence_data.xml`, `datas/ni_service_category_data.xml`, and `datas/ni_service_type_data.xml` seed identifiers and
  service vocabularies.
- `views/ni_service_request_views.xml`, `views/ni_service_event_views.xml`, and
  `views/ni_encounter_service_attendance_views.xml` provide the main operational UI.
- `views/ni_patient_portal_templates.xml` and `report/summary_report.xml` expose service information in patient-facing and
  summary outputs.

## Security and Dependencies

- `security/ir.model.access.csv` grants model permissions.
- `security/ir_rules_data.xml` constrains service record visibility.
- The module depends on `ni_patient`, `calendar`, `ni_timing`, and `ni_body_site`.

## Verification

- Review `ni_service/tests/test_encounter_service_attendance.py` after changes to request matching, attendance creation, or
  period logic.
- Re-check service request, service event, calendar attendance, and portal or summary flows after changing service scheduling
  behavior.
