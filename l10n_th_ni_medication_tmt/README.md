# Medication - TMT (`l10n_th_ni_medication_tmt`)

## Purpose

Adds Thai Medicines Terminology (TMT) coding-system records and lightweight medication parsing behavior for TMT GPU items. It is
a localization layer for `ni_medication`, not a full importer.

## Main Components

- `ni.medication` extension Adds direct `code` and `system_id` fields.
- GPU name processing `_process_name()` and `_process_gpu_name()` derive numerator/denominator dosage fields from medication
  names ending with `(GPU)`.
- Unit lookup `_search_unit()` reuses matching `uom.uom` records by `name` or `alias`, or creates one in the generic unit
  category.

## Data

- Seeds `ni.coding.system` records for `TMT | TPU` and `TMT | GPU`.

## Dependencies

- `ni_medication`

## Notes

- A medication whose name matches `%(GPU)` is forced onto the seeded GPU coding system by `_check_system()`.
- The repository contains a `wizard` package directory, but no import wizard source file is currently shipped with the module.
