# ICD-9-CM Procedure Classification (`l10n_th_icd9cm`)

## Purpose

Thai localization module that adds ICD-9-CM procedure coding support on top of `ni_procedure`. It introduces procedure chapters,
improves code lookup, and ships ICD-9-CM master data under a dedicated coding system record.

## Main Components

- `ni.procedure.chapter` New coding model used to organize ICD-9-CM procedures into chapters.
- `ni.procedure.code` extension Adds `chapter_id`, indexed `code_simplify`, and a uniqueness constraint on
  `(system_id, code, name)`.

## Data and Views

- Seeds `ni.coding.system` record `ICD-9-CM`.
- Loads procedure chapter data and bundled procedure-code data.
- Adds chapter action/menu plus chapter form, tree, and search views.
- Extends procedure-code views with chapter grouping, search-panel filtering, and dotless code lookup.

## Dependencies

- `ni_procedure`

## Notes

- The manifest loads procedure-code data from `data/ni_procedure_code_data.xml` through the `demo` key, so availability depends
  on how the module is installed in the target environment.
