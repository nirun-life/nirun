# Allergy (`ni_allergy`)

Odoo 16.0 module that records patient allergies and intolerances for Nirun. It tracks allergy substances, reactions,
criticality, and status so clinical teams can surface safety alerts in patient and encounter flows.

## Purpose

`ni_allergy` adds structured allergy and intolerance records to the core patient model. It is designed for clinically
significant alerts rather than general free-text notes, with coded substances and reaction history tied to the patient chart.

## Main Models

| Model                 | Role                                         |
| --------------------- | -------------------------------------------- |
| `ni.allergy`          | Core allergy or intolerance record           |
| `ni.allergy.code`     | Substance terminology dictionary             |
| `ni.allergy.reaction` | Reaction history linked to an allergy record |

## Data, Views, and Reports

- `views/ni_allergy_views.xml` and `views/ni_allergy_code_views.xml` provide the main allergy UI and coded dictionary
  management.
- `views/ni_patient_views.xml` and `views/ni_encounter_views.xml` surface allergies in patient and encounter contexts.
- `views/ni_patient_portal_templates.xml` exposes allergy data in the portal.
- `report/summary_report.xml` includes allergy content in the patient summary output.

## Security and Dependencies

- `security/ir.model.access.csv` grants model permissions.
- `security/ni_allergy_rule.xml` constrains allergy visibility.
- The module depends on `ni_patient`.

## Verification

- Re-check patient, encounter, and portal allergy displays after changing coded substances, state transitions, or reaction
  logic.
- Confirm the patient-level uniqueness behavior for `(patient_id, code_id)` still matches the intended alert workflow after
  schema changes.
