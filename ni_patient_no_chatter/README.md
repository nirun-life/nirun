# Patients - No Chatter (`ni_patient_no_chatter`)

Odoo 16.0 module that adds a context-driven way to open patient and encounter forms without the standard chatter pane.

## Purpose

`ni_patient_no_chatter` supports streamlined patient and encounter screens for users or devices where the messaging and activity
sidebar is unnecessary noise.

## Main Models

| Model          | Role                                                |
| -------------- | --------------------------------------------------- |
| `ni.patient`   | Adds a form reopen action that toggles `no_chatter` |
| `ni.encounter` | Adds the same no-chatter toggle for encounter forms |

## Behavior and Views

- `model/ni_patient.py` and `model/ni_encounter.py` each provide `action_no_chatter_toggle()` to reopen the current form with a
  flipped `no_chatter` context flag.
- `views/ni_patient_views.xml` and `views/ni_encounter_views.xml` adapt the forms to respect that context flag and hide chatter
  when requested.

## Dependencies

- `ni_patient`

## Verification

- Re-check the toggle flow on both patient and encounter forms to confirm the context flips cleanly between chatter and
  no-chatter layouts.
