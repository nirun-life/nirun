# Patients Location (Thai Localization) (`l10n_th_ni_patient_address`)

## Purpose

Extends Thai patient registration with structured Thai address lookup and smart-card address enrichment. It connects patient and
smart-card address data to `res.city` and `res.city.zip` records from the Thai base-location stack.

## Main Components

- `ni.patient.smartcard` extension Adds `city_id`, `zip_id`, `state_id`, and `country_id`, then enriches parsed smart-card data
  by resolving Thai locality names to `res.city`.
- `res.city.zip` extension Adds indexed `display_name`, custom split-token name search, optional code search via `/####` or
  `/######`, and Thai-first `name_get()` formatting.

## Views

- Patient form: replaces the standard free-text address inputs with `zip_id` lookup and hides the base `street2`, `city`,
  `state_id`, `zip`, and `country_id` widgets.
- Smart-card form: shows resolved city, state, country, and zip values next to the parsed address.

## Dependencies

- `l10n_th_ni_patient`
- `l10n_th_base_location`

## Notes

- Smart-card parsing normalizes Thai locality prefixes before searching `res.city`.
- The module assumes the target city has at least one related zip record when it fills `zip_id`.
