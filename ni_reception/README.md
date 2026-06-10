# Reception (`ni_reception`)

Odoo 16.0 module that provides a reception workspace for patient check-in, quick registration, vitals capture, and encounter
creation.

## Purpose

`ni_reception` is the front-desk intake layer for Nirun. It combines demographic capture, existing partner or patient lookup,
triage details, coverage selection, allergies, chronic conditions, and initial vital signs into one reception record that can
create or update a patient and open the encounter.

## Main Models

| Model          | Role                                                              |
| -------------- | ----------------------------------------------------------------- |
| `ni.reception` | Reception intake record that creates or updates patient/encounter |

## Workflow and Behavior

- `models/ni_reception.py` combines demographic fields, coverage selection, chronic condition codes, allergy codes, triage
  priority, and observation mixins for vital signs and blood group data.
- Selecting `partner_id` backfills the intake form from an existing contact and, when available, reuses the matching patient in
  the same company to avoid duplicate patient creation.
- `action_submit()` creates a new `ni.patient` when needed, creates or updates the linked `ni.encounter`, then opens the
  encounter form as the next step in the workflow.
- The module reuses `ni_condition.class_patient_state` when converting chronic condition selections into patient conditions.

## Views, Assets, and Security

- `views/ni_reception_views.xml` defines the reception intake UI.
- `views/ni_encounter_views.xml` links the reception flow with the encounter interface.
- `static/src/views/register_views.esm.js` and `static/src/views/register_views.xml` customize backend registration views.
- `security/ni_reception_group.xml`, `security/ni_reception_rules.xml`, and `security/ir.model.access.csv` define reception
  access and record rules.

## Dependencies

- `partner_age`
- `partner_gender`
- `ni_patient`
- `ni_condition`
- `ni_allergy`
- `ni_observation`
- `ni_practitioner`
- `ni_coverage`

## Verification

- Re-check intake for both new and existing patients, including partner backfill and duplicate-prevention behavior.
- Confirm submitted receptions create or update the expected patient and encounter data, including selected allergies,
  conditions, coverage, and vital signs.
- Review the custom registration view after any frontend asset change.
