# Nirun - Coding

`ni_coding` provides the coding-system foundation used by Nirun clinical modules. It stores reusable terminology systems and
codes, and it supplies a small scaffold for building FHIR-style coded resources instead of hard-coding free text.

## Scope

This module owns:

- the abstract `ni.coding` base model for coding records
- the concrete `ni.coding.system` model for terminology systems
- an `ir.model` extension that can list and open all non-abstract models that inherit from `ni.coding`
- menu entries and fallback views for browsing coding records
- seed records for common terminology systems used across the repository

## Core Models

| Model              | Type                   | Purpose                                                                                                                             |
| ------------------ | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `ni.coding`        | `models.AbstractModel` | Shared base for coded resources. Implements display naming, search, sequence ordering, duplicate-copy behavior, and fallback views. |
| `ni.coding.system` | `models.Model`         | Terminology-system master list with a name, URL, sequence, and active flag.                                                         |
| `ir.model`         | inherited model        | Adds helpers to open records and to list all concrete `ni.coding` descendants.                                                      |

`ni.coding` centralizes the common behavior for downstream models:

- default view scaffolding for form, tree, search, and kanban views
- name formatting options such as code, abbreviation, and parent path display
- a shared `sequence` field and default ordering
- copy semantics that preserve uniqueness by appending `(copy)`

## Views And Menus

The module installs a small Coding menu under `base.menu_custom` with two entries:

- `Models` opens the list of concrete coding models derived from `ni.coding`
- `Coding System` opens the terminology-system master list

The following view files are part of the module contract:

- `views/ni_coding_default_form.xml`
- `views/ni_coding_default_tree.xml`
- `views/ni_coding_default_search.xml`
- `views/ni_coding_default_kanban.xml`
- `views/ni_coding_system_views.xml`
- `views/ir_model_views.xml`

`ni.coding` falls back to the default view files when a coding model has no dedicated view or when a user does not have write
access to the form view.

## Seed Data

`data/ni_coding_system_data.xml` seeds the shared terminology systems used by the module and downstream add-ons:

- `Other`
- `Internal`
- `HL7 FHIR`
- `HL7`
- `HL7 V2`
- `HL7 V3`
- `LOINC`
- `SNOMED`
- `DICOM`
- `UCUM`

## Dependencies

- `base`
- `mail`

## Notes

- `ni.coding.system` enforces uniqueness on both `name` and `url`.
- `ni.coding` enforces uniqueness of `(system_id, name)` and `(system_id, code)`.
- Search on both models matches the human name plus the code fields they expose.
- The module is intended to be extended by other clinical modules that need stable coded terminology.
