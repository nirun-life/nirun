# Patients Thai Localization - Firstname and Lastname (`l10n_th_ni_patient_firstname`)

> **Retired (decision D12, nirun-life/nirun#194).** This module is not ported to 17.0, 18.0 or 19.0. Patients keep the single
> `res.partner.name` field. It is uninstalled at the 19.0 cutover together with `partner_firstname` (nirun-life/nirun#211),
> after a copy of the first and last names.

## Purpose

Small Thai UI localization for repositories that use `ni_patient_firstname`. It only adjusts patient-name field order on the
form view.

## Views

- Inherits `ni_patient_firstname.ni_patient_view_form_inherit`.
- Moves `lastname` so it appears immediately after `firstname`.

## Dependencies

- `ni_patient_firstname`

## Notes

- This module does not add models, fields, or security rules. Its scope is limited to form layout.
