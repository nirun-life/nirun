# Condition (`ni_condition`)

Odoo 17.0 module that implements FHIR-style patient conditions and diagnoses for Nirun.
It records persistent problems, encounter diagnoses, verification states, and condition
categories so clinical teams can track active and historical diagnoses in structured
form.

## Purpose

`ni_condition` extends the core patient and observation stack with diagnosis-oriented
records. It supports both long-lived problem tracking and encounter-linked diagnoses,
while keeping terminology aligned with shared coding dictionaries.

## Main Models

| Model                         | Role                                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------- |
| `ni.condition`                | Core patient condition record                                                         |
| `ni.condition.latest`         | SQL view: newest shown condition per patient and code (plain model, explicit columns) |
| `ni.condition.code`           | Code dictionary for condition terms                                                   |
| `ni.condition.category`       | Condition category vocabulary                                                         |
| `ni.condition.verification`   | Verification-status vocabulary                                                        |
| `ni.encounter.diagnosis`      | Encounter-specific diagnosis record, `_inherits` `ni.condition`                       |
| `ni.encounter.diagnosis.role` | Diagnosis-role vocabulary for encounter use                                           |

## Data, Views, and Reports

- `data/ni_condition_category_data.xml`, `data/ni_condition_verification_data.xml`, and
  `data/ni_encounter_diagnosis_role_data.xml` seed the supporting vocabularies.
- `views/ni_condition_views.xml`, `views/ni_encounter_diagnosis_views.xml`, and the
  related code/category/verification views provide the clinical UI.
- `views/ni_patient_views.xml`, `views/ni_encounter_views.xml`, and
  `views/ni_patient_portal_templates.xml` surface condition data in patient, encounter,
  and portal contexts.
- `report/summary_report.xml` adds condition information to summary reporting.

## Display Names

- `ni.condition`: the context keys `show_code`, `show_patient`, `show_severity` and
  `show_state` extend the name; `ni.condition.latest` shows the same name.
- `ni.condition.code`: as `ni.coding`, but `show_code` puts the code first.
- `ni.condition.verification`: `Parent, Name`.

## Security and Dependencies

- `security/ir.model.access.csv` grants model permissions.
- `security/condition_rules.xml` constrains condition visibility.
- The module depends on `ni_patient` and `ni_observation`.

## Verification

- Re-check patient, encounter, and portal condition displays after changing diagnosis
  models, rules, or summary output.
- `tests/` covers the display names, the patient/code constraint, the hierarchies, the
  latest view, and the encounter diagnoses (count, role limit, confirm, toggle).
