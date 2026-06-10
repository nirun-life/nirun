# Reception (Thai Localization) (`l10n_th_ni_reception`)

## Purpose

Thai localization for reception intake. The module adds Thai address lookup and a single selected coverage field to
`ni.reception`, then maps those values into patient and encounter creation flows.

## Main Components

- `ni.reception` extension Adds computed editable `zip_id`, `city_id`, `state_id`, `country_id`, `city`, `zip`, and
  `coverage_type_id`.
- Address consistency checks `_check_zip()` validates that the selected zip, city, state, country, and zip text remain aligned.
- Reception-to-patient and reception-to-encounter propagation `_get_patient_field()` adds `zip_id` and `city_id`;
  `_get_encounter_field()` adds `coverage_type_id`.

## Views

- Reception form: adds `zip_id` address lookup, hides the base address widgets, shows a single `coverage_type_id`, and hides the
  original `coverage_type_ids` widget.

## Dependencies

- `ni_reception`
- `l10n_th_ni_patient_address`
- `l10n_th_ni_coverage`

## Notes

- The module is `auto_install=True`, so Odoo installs it automatically once all dependencies are present.
- `coverage_type_id` is derived from the first entry in `coverage_type_ids` unless the user selects a different allowed child
  coverage.
