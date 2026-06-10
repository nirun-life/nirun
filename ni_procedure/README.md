# Procedure (`ni_procedure`)

Odoo 16.0 module that implements structured clinical procedures for Nirun. It tracks performed procedures, their categories and
outcomes, and exposes them in patient and encounter contexts for the shared clinical timeline.

## Purpose

`ni_procedure` covers completed interventions such as surgeries or other clinical procedures. It builds on the patient workflow
foundation so performed procedures can be recorded with consistent coding, outcomes, and encounter linkage.

## Main Models

| Model                   | Role                             |
| ----------------------- | -------------------------------- |
| `ni.procedure`          | Core procedure record            |
| `ni.procedure.code`     | Procedure terminology dictionary |
| `ni.procedure.category` | Procedure category vocabulary    |
| `ni.procedure.outcome`  | Procedure outcome vocabulary     |

## Data and Views

- `data/ir_sequence_data.xml` provides procedure sequencing support.
- `data/ni_procedure_category_data.xml` and `data/ni_procedure_outcome_data.xml` seed the supporting vocabularies.
- `views/ni_procedure_views.xml`, `views/ni_procedure_code_views.xml`, `views/ni_procedure_category_views.xml`, and
  `views/ni_procedure_outcome_views.xml` provide the main UI.
- `views/ni_encounter_views.xml` exposes procedures from the encounter form.

## Security and Dependencies

- `security/ni_procedure_group.xml` defines procedure access groups.
- `security/ni_procedure_security.xml` and `security/ir.model.access.csv` control permissions and record visibility.
- The module depends on `ni_patient` and `mail`.

## Verification

- Re-check encounter procedure flows and terminology views after changing coded fields, permissions, or sequence behavior.
