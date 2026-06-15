# Service (`ni_service`)

`ni_service` is the Nirun Odoo 16.0 module for healthcare service cataloging, service requests, scheduled service delivery, and
encounter attendance tracking. It bridges clinical requests with `calendar.event` records and keeps the service timeline linked
to patients, encounters, and requests.

## What This Module Owns

- Service catalog records and vocabularies.
- Service requests that follow the workflow/timing/period stack used by other clinical request models.
- Calendar-backed service events.
- Encounter attendance records that can be matched back to the originating request.
- Small extensions to related Odoo models such as `calendar.event`, `res.company`, `hr.job`, and `resource.calendar.attendance`.
- Company-level control over whether services can belong to multiple categories.
- Service categories and service types that can be either company-private or shared across companies.

## Core Models

| Model                             | Role                                                                                            |
| --------------------------------- | ----------------------------------------------------------------------------------------------- |
| `ni.service`                      | Service catalog record with calendar, attendance, employee, encounter, and multi-category links |
| `ni.service.category`             | Service category vocabulary with optional company ownership and membership across services      |
| `ni.service.type`                 | Service type vocabulary with optional company ownership                                         |
| `ni.service.request`              | Requested service workflow                                                                      |
| `ni.service.event`                | Service delivery event backed by `calendar.event`                                               |
| `ni.encounter.service.attendance` | Encounter attendance linked to a service event or request                                       |

## Maintainer Quick Reference

```text
Service catalog
  `ni.service`
      |-- category/type vocabularies
      |-- default calendar + attendance templates
      |-- employee and encounter links
      v
Service request
  `ni.service.request`
      |-- workflow + timing + identifier + period
      |-- service selection and patient context
      v
Service event
  `ni.service.event`
      |-- inherits `calendar.event`
      |-- single/multi service scheduling
      |-- calendar, attendee, attachment, and patient planning
      v
Encounter attendance
  `ni.encounter.service.attendance`
      |-- ties encounter + attendance + service + request
      |-- auto-matches the originating request when possible
      v
Encounter timeline / reporting
  `ni.encounter`
  portal templates
  summary report
```

## Menu Map

| Menu                                 | Action                                 | Intent                                                                            |
| ------------------------------------ | -------------------------------------- | --------------------------------------------------------------------------------- |
| `Service > Service`                  | `ni_service.ni_service_action`         | Open the service catalog and create/edit individual services                      |
| `Service > Configuration > Routine`  | `ni_service.ni_service_routine_action` | Manage the routine-service subset                                                 |
| `Service > Configuration > Category` | `ni_service_category_action`           | Maintain service category vocabulary                                              |
| `Service > Configuration > Type`     | `ni_service_type_action`               | Maintain service type vocabulary                                                  |
| `Calendar > Service Calendar`        | `ni_service_event_action`              | Work with scheduled service events in calendar/tree/kanban/pivot/graph/form views |
| `Calendar > Personal Calendar`       | `calendar.action_calendar_event`       | Fall back to the standard personal calendar                                       |

## Views And Rules

| Model                             | Main view types                                          | Notes                                                                                |
| --------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `ni.service`                      | tree, form, search                                       | Catalog browsing, calendar assignment, attendance templates, practitioner assignment |
| `ni.service.request`              | tree, kanban, form                                       | Request entry and event follow-up                                                    |
| `ni.service.event`                | calendar, tree, kanban, pivot, graph, form, quick-create | Scheduling, planning, analytics, and fast creation                                   |
| `ni.encounter.service.attendance` | tree, kanban, form                                       | Encounter-service bridge and request matching                                        |
| `ni.service.category`             | tree, form, search                                       | Category vocabulary maintenance                                                      |
| `ni.service.type`                 | tree, form, search                                       | Type vocabulary maintenance                                                          |

| View                                              | Modified by                                    | Why                                                                        |
| ------------------------------------------------- | ---------------------------------------------- | -------------------------------------------------------------------------- |
| `ni_patient.ni_encounter_class_view_form`         | `views/ni_encounter_views.xml`                 | Adds service calendar defaults to encounter class setup                    |
| `ni_patient.ni_encounter_view_form`               | `views/ni_encounter_views.xml`                 | Adds generated service resources and linked service requests to encounters |
| `base.view_company_form`                          | `views/res_company_views.xml`                  | Adds company-level default service calendar and attendance templates       |
| `resource.view_resource_calendar_attendance_form` | `views/resource_calendar_attendance_views.xml` | Exposes linked services on calendar attendance records                     |
| `resource.view_resource_calendar_attendance_tree` | `views/resource_calendar_attendance_views.xml` | Adds quick edit access from the attendance list                            |
| `ni_patient.portal_my_patient_encounter`          | `views/ni_patient_portal_templates.xml`        | Shows service attendance details in the patient portal encounter view      |

| Key behavior                                                                  | Why it matters                                                                                |
| ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `ni.service.request` inherits workflow, timing, identifier, and period mixins | Request changes can affect shared clinical workflow logic                                     |
| `ni.service.event` uses `_inherits = {"calendar.event": "event_id"}`          | Calendar behavior is shared, so service changes must respect Odoo event semantics             |
| `ni.service` keeps `category_id` and `category_ids` aligned                   | `category_ids` is the membership field; `category_id` remains the primary compatibility field |
| `ni.service.category` / `ni.service.type` use optional `company_id`           | Blank means shared; a set company means private to that company                               |
| Shared `ni.service.category` / `ni.service.type` records are admin-managed    | Non-admin users may manage only company-private vocabulary records                            |
| `ni.service.event` keeps `service_id`, `service_ids`, and mode aligned        | Dual service selectors can drift if constraints are changed carelessly                        |
| `ni.service.event` constrains calendar/attendance combinations                | Invalid combinations can clear data or raise user errors                                      |
| `ni.encounter.service.attendance` auto-matches a request                      | Matching depends on patient, service, and period alignment                                    |
| `ni.service` and `ni.service.event` are multi-company scoped                  | Visibility depends on company context, not global access                                      |
| `res.company.service_multi_category` defaults to enabled                      | Disable only for legacy single-category workflows                                             |
| `ir.cron` backfill job is scheduled for install time + 3 minutes              | It can be run once and deactivates itself after populating legacy membership                  |

## Security And Dependencies

- `security/ir.model.access.csv` grants model permissions.
- `security/ir.rules_data.xml` constrains service record visibility.
- Dependencies: `ni_patient`, `calendar`, `ni_timing`, and `ni_body_site`.

## Permission Matrix

| Model                             | ACL access                                                                                 | Rule / visibility                                         | Notes                         |
| --------------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------- | ----------------------------- |
| `ni.service`                      | read for everyone; full access for `ni_patient.group_user` and `ni_patient.group_admin`    | multi-company: `company_id in company_ids`                | Core service catalog          |
| `ni.service.category`             | read for everyone; full access for `ni_patient.group_manager` and `ni_patient.group_admin` | shared records admin-only; private records company-scoped | Coding vocabulary             |
| `ni.service.type`                 | read for everyone; full access for `ni_patient.group_manager` and `ni_patient.group_admin` | shared records admin-only; private records company-scoped | Coding vocabulary             |
| `ni.service.request`              | full access for `ni_patient.group_user`                                                    | no module-specific record rule                            | Request workflow              |
| `ni.service.event`                | full access for `ni_patient.group_user`                                                    | multi-company: `company_id in company_ids`                | Calendar-backed service event |
| `ni.encounter.service.attendance` | full access for everyone                                                                   | no module-specific record rule                            | Encounter attendance bridge   |

## Dependency And Extension Map

| Base model                     | Extension                      | Why it exists                                                                           |
| ------------------------------ | ------------------------------ | --------------------------------------------------------------------------------------- |
| `calendar.event`               | `models/ni_service_event.py`   | Exposes public attendee data safely and backs `ni.service.event` through `_inherits`    |
| `res.company`                  | `models/res_company.py`        | Stores default service calendar and default service attendance templates                |
| `hr.job`                       | `models/hr_job.py`             | Gives service-related job records a color for UI grouping                               |
| `resource.calendar.attendance` | `models/resource_calendar.py`  | Links calendar attendances back to services and provides a custom edit action           |
| `ni.encounter`                 | `models/ni_encounter.py`       | Adds service-calendar context, generated service attendances, and service request links |
| `ni.encounter.class`           | `models/ni_encounter_class.py` | Adds default service calendar and default services for encounter classes                |
