# Patients - Firstname and Lastname (`ni_patient_firstname`)

Odoo 16.0 auto-installed addon that adapts the patient form to use split first-name and last-name fields from
`partner_firstname`.

## Purpose

`ni_patient_firstname` aligns Nirun patient entry with deployments that manage contact names as structured first and last names
instead of a single editable `name` field.

## Main Behavior

- `views/ni_patient_views.xml` makes the inherited `name` field read-only on the patient form.
- The same view adds `firstname` and `lastname` fields and requires at least one of them so the partner name can still be built
  correctly.
- The module is `auto_install=True`, so it activates automatically when both `ni_patient` and `partner_firstname` are present.

## Dependencies

- `ni_patient`
- `partner_firstname`

## Verification

- Re-check patient creation and editing to confirm first and last name entry updates the derived display name correctly.
- Confirm the module only activates in environments where `partner_firstname` is installed.
