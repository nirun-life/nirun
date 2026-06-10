# Nirun - Coding

Odoo 16.0 module that provides the coding-system foundation for Nirun clinical data. It stores reusable clinical code systems
and their codes so downstream modules can bind to FHIR-style terminology rather than hard-coded free text.

## Purpose

`ni_coding` is the shared base for clinical coding systems such as ICD, SNOMED, and LOINC. It is intentionally small and is
meant to be depended on by other clinical modules that need stable code records, code-system metadata, or references to
`ir.model`.

## Main Models

| Model                | Role                                              |
| -------------------- | ------------------------------------------------- |
| `ni.coding.system`   | Master list of supported coding systems           |
| `ni.coding`          | Individual code record inside a coding system     |
| `ir.model` extension | Links Odoo models to coding metadata where needed |

## Data and Views

- `data/ni_coding_system_data.xml` seeds the initial coding-system records.
- `views/ni_coding_system_views.xml` and `views/ni_coding_default_*` expose the core coding records in list, kanban, search, and
  form views.
- `views/ir_model_views.xml` adds model-level integration points for code-aware workflows.

## Dependencies

- `base`
- `mail`

## Verification

- Confirm the coding-system menu and seeded records load cleanly after module update.
- Re-check downstream modules that depend on shared code records after changing terminology or seed data.
