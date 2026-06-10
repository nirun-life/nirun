# Patients - Birthdate Est. (`ni_patient_birthdate_est`)

Odoo 16.0 module that marks estimated birthdates explicitly and normalizes them to `1 January` when the exact day and month are
unknown.

## Purpose

`ni_patient_birthdate_est` adds a durable flag for approximate dates of birth so patient and encounter workflows can distinguish
between exact dates and year-only estimates.

## Main Models

| Model          | Role                                                    |
| -------------- | ------------------------------------------------------- |
| `res.partner`  | Stores the estimate flag and SQL constraint             |
| `ni.patient`   | Exposes the estimate flag through the patient record    |
| `ni.encounter` | Keeps the same onchange behavior in encounter workflows |

## Behavior

- `models/res_partner.py` adds `birthdate_estimate` and enforces a database constraint requiring estimated birthdates to use day
  `1`.
- Onchange handlers in `res.partner`, `ni.patient`, and `ni.encounter` normalize the date to `1 January` of the selected year
  whenever the estimate flag is turned on.
- `views/ni_patient_views.xml` exposes the estimated-birthdate behavior in the patient form.

## Dependencies

- `ni_patient`

## Verification

- Re-check patient and encounter forms to confirm enabling the estimate flag rewrites the date to `1 January`.
- Confirm records with estimated birthdates cannot violate the SQL constraint.
