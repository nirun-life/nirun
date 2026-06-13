# Related Person (`ni_related_person`)

`ni_related_person` records patient family members and other related people in Nirun Odoo 16.0. It links related contacts to a
patient using structured relationship coding and optional period fields, while reusing `res.partner` as the underlying contact.

## What This Module Owns

- Structured related-person records for a patient.
- Relationship vocabulary for coding family or caregiver roles.
- Patient-side access to related people from the main patient form.

## Core Models

| Model                       | Role                                             |
| --------------------------- | ------------------------------------------------ |
| `ni.patient.related.person` | Related-person record, `_inherits` `res.partner` |
| `ni.patient.relationship`   | Relationship vocabulary                          |

## Maintainer Quick Reference

```text
Patient
  `ni.patient`
      |-- related person counter + one2many lines
      v
Related person
  `ni.patient.related.person`
      |-- `_inherits` `res.partner`
      |-- patient link + relationship codes + period mixin
      |-- default patient linking from patient context
      |-- self-reference protection + address copy helper
      v
Relationship vocabulary
  `ni.patient.relationship`
      |-- coding dictionary based on `ni.coding`
```

## Menu Map

| Menu               | Action | Intent                                                                            |
| ------------------ | ------ | --------------------------------------------------------------------------------- |
| No standalone menu | N/A    | This module is accessed from the patient form and relationship dictionary screens |

## Integration Map

| Integration point                                                       | What it does                                              | Why it matters                                                     |
| ----------------------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------ |
| `ni_patient.ni_patient_view_form`                                       | Adds the Related Person tab and related-person counter    | This is the primary user entry point for the module                |
| `ni.patient.related.person` `_inherits = {"res.partner": "partner_id"}` | Reuses contact fields from `res.partner`                  | Related people behave like contacts while staying patient-scoped   |
| `default_get` on `ni.patient.related.person`                            | Pulls `patient_id` from active patient context            | Creating from the patient form should bind automatically           |
| `action_copy_parent_address`                                            | Copies the patient address into the related person        | Useful for dependents/caregivers sharing the same address          |
| `_check_no_recursive`                                                   | Blocks self-referential patient/partner links             | Prevents a patient from being related to themselves                |
| `ni.patient.relationship` inherits `ni.coding`                          | Reuses the shared coding structure for relationship types | Keeps relationship values aligned with the rest of the code system |

## Security And Dependencies

- `security/ir.model.access.csv` grants model permissions.
- Dependencies: `ni_patient`.

## Permission Matrix

| Model                       | ACL access                                                  | Rule / visibility              | Notes                    |
| --------------------------- | ----------------------------------------------------------- | ------------------------------ | ------------------------ |
| `ni.patient.related.person` | read for everyone; full access for `ni_patient.group_user`  | no module-specific record rule | Patient-related contacts |
| `ni.patient.relationship`   | read for everyone; full access for `ni_patient.group_admin` | no module-specific record rule | Relationship vocabulary  |

## Common Pitfalls

- `partner_id` and `patient_id` are linked by `_inherits` plus patient context; do not break the default patient binding.
- Self-reference protection is intentional and should stay in place when changing partner logic.
- Address copying uses the patient partner fields; changes to partner address structure can affect that helper.
- The module is patient-form driven, so changes to `ni.patient` views are part of the module surface.
