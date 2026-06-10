# Related Person (`ni_related_person`)

Odoo 16.0 module that records patient family members and other related people for Nirun. It links related contacts to a patient
with structured relationship coding and optional period fields, while reusing `res.partner` as the underlying contact record.

## Purpose

`ni_related_person` adds structured people-around-the-patient data to the chart. It is intended for family, caregivers, or other
relevant contacts that should be linked explicitly to the patient record with coded relationship labels.

## Main Models

| Model                       | Role                                             |
| --------------------------- | ------------------------------------------------ |
| `ni.patient.related.person` | Related-person record, `_inherits` `res.partner` |
| `ni.patient.relationship`   | Relationship vocabulary                          |

## Data and Views

- `data/ni.patient.relationship.csv` seeds the relationship vocabulary.
- `views/ni_patient_related_person.xml` provides the related-person UI from the patient context.
- `views/ni_patient_relationship_views.xml` exposes relationship dictionary management.
- `views/ni_patient_views.xml` surfaces related people from the patient form.

## Security and Dependencies

- `security/ir.model.access.csv` grants model permissions.
- The module depends on `ni_patient`.

## Verification

- Re-check patient-side related-person creation from context, especially the default patient linking behavior.
- Confirm self-reference protection and address-copy behavior still work after changing related-person fields or partner
  inheritance.
