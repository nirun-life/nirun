# Appointment (`ni_appointment`)

Odoo 16.0 module that manages patient appointments, follow-up scheduling, portal access, cancellation reasons, and appointment
printouts on top of Odoo Calendar and Nirun encounter workflows.

## Purpose

`ni_appointment` provides the scheduling layer for planned patient visits. It links calendar events to patients and encounters,
tracks appointment state through the request workflow mixin, and supports operational follow-up flows such as rescheduling,
cancellation, encounter conversion, and patient portal viewing.

## Main Models

| Model                          | Role                                                     |
| ------------------------------ | -------------------------------------------------------- |
| `ni.appointment`               | Core appointment record, `_inherits` `calendar.event`    |
| `ni.appointment.type`          | Appointment type vocabulary                              |
| `ni.appointment.instruction`   | Reusable preparation or instruction vocabulary           |
| `ni.appointment.cancel.reason` | Structured cancellation reasons                          |
| `ni.appointment.cancel.wizard` | Guided cancellation flow                                 |
| `ni.encounter`                 | Extended with appointment linkage and next-visit helpers |
| `res.company`                  | Holds default instructions and default duration          |

## Workflow and Integration

- `models/ni_appointment.py` combines `ni.workflow.request.mixin`, `ni.identifier.mixin`, and `calendar.event` inheritance so
  each appointment behaves like both a workflow request and a calendar item.
- Default values inherit company-level appointment instructions and duration settings from `models/res_company.py`.
- Appointments can carry encounter reasons, condition references from the linked encounter, performer, department, follow-up
  parentage, and cancellation metadata.
- `models/ni_encounter.py` links encounters back to their originating appointment and exposes next-appointment helpers when
  encounters close.
- `wizard/ni_appointment_cancel_wizard.py` records structured cancellation details instead of relying on ad hoc free text.

## Views, Reports, and Portal

- `views/ni_appointment_views.xml`, `views/ni_appointment_type_views.xml`, `views/ni_appointment_instruction_views.xml`, and
  `views/ni_appointment_cancel_reason_views.xml` cover appointment operations and reference data maintenance.
- `views/ni_encounter_views.xml` and `views/res_company_views.xml` connect scheduling with encounter closure and company
  defaults.
- `controllers/appointment.py`, `views/ni_appointment_portal.xml`, and `views/ni_appointment_portal_templates.xml` provide the
  patient portal listing and detail pages.
- `reports/appointment.xml` and `reports/templates.xml` define the printable appointment report.

## Dependencies

- `ni_patient`
- `ni_condition`
- `calendar`
- `portal`

## Verification

- Re-check appointment creation, activation, cancellation, and encounter handoff flows after workflow or view changes.
- Confirm portal appointment list and detail pages still load correctly after controller or template edits.
- Review the printed appointment report after changes to report templates or appointment fields.
