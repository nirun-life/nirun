# Patients - Birthdate Est. (`ni_patient_birthdate_est`)

Odoo 18.0 module that marks estimated birthdates explicitly and normalizes them to
`1 January` when the exact day and month are unknown.

## Purpose

`ni_patient_birthdate_est` adds a durable flag for approximate dates of birth so patient
and encounter workflows can distinguish between exact dates and year-only estimates.

## Main Models

| Model         | Role                                                 |
| ------------- | ---------------------------------------------------- |
| `res.partner` | Stores the estimate flag and SQL constraint          |
| `ni.patient`  | Exposes the estimate flag through the patient record |

## Behavior

- `models/res_partner.py` adds `birthdate_estimate` and enforces a database constraint
  requiring estimated birthdates to use day `1`.
- The constraint checks the day only, not the month. The flag is not required: partners
  older than the module have no value.
- An onchange in `ni.patient` normalizes the date to `1 January` of the selected year
  when the estimate flag is turned on. The encounter form does not show the flag, so
  `ni.encounter` and `res.partner` have no onchange of their own.
- `views/ni_patient_views.xml` shows the flag next to the birthdate of the patient form.

## Dependencies

- `ni_patient`

## Verification

- Re-check the patient form to confirm enabling the estimate flag rewrites the date to
  `1 January`.
- Confirm records with estimated birthdates cannot violate the SQL constraint.
