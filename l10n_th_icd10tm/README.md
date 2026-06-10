# ICD-10-TM (`l10n_th_icd10tm`)

## Purpose

Thai localization module that adds the ICD-10-TM coding system to Nirun condition management. It extends `ni.condition` with
Thai diagnosis chapters, blocks, code search helpers, and encounter diagnosis-role data aligned to the seeded ICD-10-TM system.

## Main Components

- `ni.condition.chapter` Stores ICD-10-TM chapters as `ni.coding` records and exposes `block_ids`.
- `ni.condition.block` Stores chapter blocks with parent/child hierarchy support through `_parent_store`.
- `ni.condition.code` extension Adds `chapter_id`, `block_id`, `type`, and indexed `code_simplify` for dotless code lookup.

## Data and Views

- Seeds `ni.coding.system` record `ICD-10-TM`.
- Loads chapter and block master data from XML.
- Replaces the default encounter diagnosis-role setup by deactivating the base roles and creating ICD-10-TM-oriented roles such
  as `PDx`, `SDx`, `Comorbidity`, `Complication`, `Other`, and `External Cause`.
- Adds standalone menus and form/tree/search views for chapters and blocks.
- Extends condition-code search, form, and tree views with chapter/block grouping and code/header type handling.

## Dependencies

- `ni_condition`

## Notes

- The module provides chapter and block scaffolding plus search behavior. Condition-code master data is not loaded by default;
  the repository keeps sample code data under `demo/`.
