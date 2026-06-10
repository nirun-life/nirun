# Coverage (`ni_coverage`)

Odoo 16.0 module that records patient insurance coverage, coverage type, co-pay structure, and insurance plans for Nirun. It
provides structured benefit and policy data so patient financial coverage can be linked to the clinical record.

## Purpose

`ni_coverage` stores the patient-side representation of healthcare coverage. It combines identifier and period support with
insurance-plan metadata and benefit lines so the care team can track coverage status, subscriber details, and beneficiary costs.

## Main Models

| Model                       | Role                                    |
| --------------------------- | --------------------------------------- |
| `ni.coverage`               | Core patient coverage record            |
| `ni.coverage.type`          | Coverage type vocabulary                |
| `ni.coverage.copay`         | Co-pay vocabulary                       |
| `ni.insurance.plan`         | Insurance plan master record            |
| `ni.coverage.benefit`       | Coverage-specific beneficiary cost line |
| `ni.insurance.plan.benefit` | Insurance-plan benefit definition       |
| `ni.coverage.benefit.base`  | Shared benefit-line base model          |

## Data and Views

- `data/coverage_type_data.xml`, `data/coverage_copay_data.xml`, and `data/ir_sequence_data.xml` seed the core coverage
  vocabularies and identifiers.
- `views/ni_coverage_views.xml`, `views/ni_insurance_plan_views.xml`, `views/ni_coverage_type_views.xml`, and
  `views/ni_coverage_copay_views.xml` provide the main coverage and plan UI.
- `views/ni_patient_views.xml` and `views/ni_encounter_views.xml` surface coverage information in patient and encounter
  contexts.

## Security and Dependencies

- `security/ir.model.access.csv` grants model permissions.
- The module depends on `ni_patient`.

## Verification

- Re-check plan-to-coverage defaulting, beneficiary cost lines, and state display after changing `ni.coverage` or insurance plan
  logic.
- Confirm patient and encounter coverage displays still reflect the intended active and historical policy data.
