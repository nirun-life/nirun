# Patients - Unique (`ni_patient_unique`)

Odoo 16.0 auto-installed addon that enforces company- and nationality-scoped uniqueness for patient identification IDs.

## Purpose

`ni_patient_unique` adds a durable deduplication rule for patient identifiers so the same identification number cannot be
registered twice within the same company and nationality combination.

## Main Models

| Model        | Role                                                          |
| ------------ | ------------------------------------------------------------- |
| `ni.patient` | Stores the identification field and uniqueness SQL constraint |

## Behavior

- `models/ni_patient.py` redefines `identification_id` as a stored field.
- The module adds a SQL constraint on `(company_id, nationality_id, identification_id)` with a patient-specific error message.
- The module is `auto_install=True`, so it is intended to apply automatically alongside `ni_patient`.

## Dependencies

- `ni_patient`

## Verification

- Re-check patient creation and update flows with duplicate identification IDs in the same company and nationality.
- Confirm valid duplicates across different companies or nationalities still behave as intended for your deployment.
