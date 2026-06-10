# Patient (`ni_patient`)

Odoo 16.0 module that provides the core patient and encounter model for Nirun. It anchors the clinical data hierarchy,
patient/encounter workflow state, and shared timeline records used by the rest of the healthcare modules.

## Purpose

`ni_patient` is the central clinical module in the repository. It owns the patient record, encounter lifecycle, and the
read-only workflow timeline that combines events and requests into a single patient history.

## Main Models

| Model                                              | Role                                                                |
| -------------------------------------------------- | ------------------------------------------------------------------- |
| `ni.patient`                                       | Central patient record, `_inherits` `res.partner`                   |
| `ni.encounter`                                     | Patient visit/admission, `_inherits` `ni.patient`                   |
| `ni.patient.res`                                   | Abstract mixin for patient-linked clinical records                  |
| `ni.workflow`                                      | Shared workflow base used by event and request records              |
| `ni.workflow.event`                                | Stored timeline mirror for completed events                         |
| `ni.workflow.request`                              | Stored timeline mirror for requested items                          |
| `ni.workflow.line`                                 | Read-only union view over events and requests                       |
| `ni.location` and related encounter support models | Location, class, participant, admit, discharge, and reason metadata |

## Workflow and Views

- `ni.workflow.event.mixin` and `ni.workflow.request.mixin` power the state transitions used by downstream clinical modules.
- `views/ni_workflow_event_views.xml`, `views/ni_workflow_request_views.xml`, and `views/ni_workflow_line_views.xml` expose the
  timeline and state history.
- `views/ni_patient_views.xml`, `views/ni_encounter_views.xml`, and the related support views define the core patient and
  encounter UI.
- Portal templates in `views/ni_patient_portal.xml` and `views/ni_patient_portal_templates.xml` expose patient-facing entry
  points.

## Security and Support Files

- `security/ni_patient_group.xml` defines the patient access group.
- `security/ni_patient_rules.xml` constrains record access.
- `security/ir.model.access.csv` grants model-level permissions.
- `data/ir_sequence_data.xml` and the other `data/*.xml` files seed encounter classes, discharge data, participant types, and
  state reasons.
- `wizard/ni_encounter_discharge_wizard_views.xml` and `wizard/ni_patient_archive_wizard_views.xml` support guided encounter and
  archive actions.

## Dependencies

- `ni_coding`
- `ni_identifier`
- `ni_period`
- `hr`
- `mail`
- `partner_age`
- `partner_gender`
- `partner_religion`
- `portal`

## Verification

- Review `ni_patient/tests/test_ni_patient.py` and `ni_patient/tests/test_ni_workflow.py` after any workflow, security, or
  portal change.
- Re-check patient, encounter, workflow timeline, and portal flows after structural changes to the core models.
