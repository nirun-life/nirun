# Thai Coverage (`l10n_th_ni_coverage`)

## Purpose

Localizes Nirun coverage handling for Thai insurance and entitlement schemes. The module seeds Thai coverage-type master data
and adds a single active coverage selector to encounters.

## Main Components

- `ni.encounter` extension Adds editable `coverage_type_id` constrained to the encounter's `coverage_type_ids` and defaults it
  to the first available coverage when patient coverage changes.

## Data and Views

- Loads a large Thai `ni.coverage.type` hierarchy, including top-level schemes and child entitlement codes.
- Extends the encounter form inherited from `ni_coverage` with a radio-widget `coverage_type_id`.

## Dependencies

- `ni_coverage`

## Notes

- This module does not change the base many-to-many coverage relation. It adds a single "use coverage" field for the encounter
  UI and downstream workflow selection.
