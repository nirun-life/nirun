# Community Care (`ni_community_care`)

Odoo 16.0 application module that extends Nirun for community-based elder and home-care workflows, including registration, needs
assessment, service planning, service event execution, approvals, and operational reporting.

## Purpose

`ni_community_care` is the community-service layer on top of the core Nirun patient model. It adapts patients, staff, services,
surveys, and care plans for field operations, geographic assignments, approval cycles, and monthly or daily reporting used by
community care programs.

## Main Models

| Model                                          | Role                                                                     |
| ---------------------------------------------- | ------------------------------------------------------------------------ |
| `ni.patient`                                   | Community-care patient profile with needs, risks, and careplan data      |
| `ni.service`                                   | Community-care service definition with category membership and targeting |
| `ni.service.event`                             | Service execution record used for visits and care delivery               |
| `ni.service.event.approval`                    | Monthly or period-based approval and payout support                      |
| `ni.careplan`                                  | Request-style care plan with community service linkage                   |
| `ni.risk.assessment`                           | Patient risk and planning records                                        |
| `ni.cc.report.monthly`                         | Monthly community-care report and line items                             |
| `ni.service.event.report`                      | Read-only service-event analysis view                                    |
| `ni.service.event.daily.report`                | Read-only daily service summary view                                     |
| `ni.my.area.mixin`                             | Reusable geographic “my area” filtering                                  |
| `ni.need`, `ni.patient.need.line`              | Need catalog and patient need history                                    |
| `ni.patient.type` and related reference models | Community-care classification vocabularies                               |

## Workflow and Structure

- `models/ni_patient.py` adds community registration fields, needs tracking, risk assessment, care plans, service-event links,
  location helpers, and warning or validation logic around age, registration date, and related community-care fields.
- `models/ni_service.py`, `models/ni_service_event.py`, and related report models adapt the generic service layer for
  community-care categories, outcomes, dashboards, and operational reporting. Service lookups in this module follow service
  category membership, not only the primary category, so multi-category services are included wherever a category match is
  expected.
- `models/ni_service_event_approval.py` provides a large approval workflow with computed aggregates, report generation, and cron
  jobs for creating, refreshing, and cleaning approval batches.
- `models/ni_my_area_mixin.py`, `models/hr_employee.py`, and `models/res_users.py` apply staff-area filtering and geographic
  assignment behavior across users, employees, and reports.
- `wizard/survey_subject.py` and the survey extensions adapt questionnaires for community-care targeting and patient type logic.

## Views, Reports, Assets, and Security

- The module ships broad backend UI coverage for patients, services, care plans, approvals, risk assessments, smartcards, and
  monthly or daily reports under `views/*.xml`.
- `report/*.xml` contains printable service, patient, careplan, and approval documents.
- `static/src/components/*`, `static/src/views/*`, and the SCSS files provide backend dashboards, headers, and visual
  customizations for community-care screens.
- `security/ir.model.access.csv` and `security/ir_rules_data.xml` define model permissions and area-aware record rules.

## Dependencies

- `ni_patient`
- `ni_service`
- `ni_condition`
- `ni_allergy`
- `ni_questionnaire`
- `ni_benefit`
- `l10n_th_ni_patient_address`
- `l10n_th_ni_patient`
- `l10n_th_ni_coverage`
- `ni_related_person`

## Verification

- Re-check patient registration, service-event entry, and approval workflows after structural changes.
- Review the cron-driven approval flow carefully after changes to `ni.service.event.approval`.
- The module has automated coverage in `tests/test_ni_my_area_mixin.py` and `tests/test_ni_service_event.py`; keep those flows
  in mind after changes to area filtering or service-event logic.
- Re-check risk-assessment seeding after category membership changes, because `ni.risk.assessment` now pulls services by
  category membership rather than a single primary category.
