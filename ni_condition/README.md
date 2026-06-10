# Condition (`ni_condition`)

Odoo 16.0 module that implements FHIR-style patient conditions and diagnoses for Nirun. It records persistent problems,
encounter diagnoses, verification states, and condition categories so clinical teams can track active and historical diagnoses
in structured form.

## Purpose

`ni_condition` extends the core patient and observation stack with diagnosis-oriented records. It supports both long-lived
problem tracking and encounter-linked diagnoses, while keeping terminology aligned with shared coding dictionaries.

## Main Models

| Model                         | Role                                                                 |
| ----------------------------- | -------------------------------------------------------------------- |
| `ni.condition`                | Core patient condition record                                        |
| `ni.condition.latest`         | Current-condition helper model layered on top of base condition data |
| `ni.condition.code`           | Code dictionary for condition terms                                  |
| `ni.condition.category`       | Condition category vocabulary                                        |
| `ni.condition.verification`   | Verification-status vocabulary                                       |
| `ni.encounter.diagnosis`      | Encounter-specific diagnosis record, `_inherits` `ni.condition`      |
| `ni.encounter.diagnosis.role` | Diagnosis-role vocabulary for encounter use                          |

## Data, Views, and Reports

- `data/ni_condition_category_data.xml`, `data/ni_condition_verification_data.xml`, and
  `data/ni_encounter_diagnosis_role_data.xml` seed the supporting vocabularies.
- `views/ni_condition_views.xml`, `views/ni_encounter_diagnosis_views.xml`, and the related code/category/verification views
  provide the clinical UI.
- `views/ni_patient_views.xml`, `views/ni_encounter_views.xml`, and `views/ni_patient_portal_templates.xml` surface condition
  data in patient, encounter, and portal contexts.
- `report/summary_report.xml` adds condition information to summary reporting.

## Security and Dependencies

- `security/ir.model.access.csv` grants model permissions.
- `security/condition_rules.xml` constrains condition visibility.
- The module depends on `ni_patient` and `ni_observation`.

## Verification

- Re-check patient, encounter, and portal condition displays after changing diagnosis models, rules, or summary output.
