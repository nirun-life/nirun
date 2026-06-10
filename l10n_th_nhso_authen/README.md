# NHSO Authen (`l10n_th_nhso_authen`)

## Purpose

Adds Thai NHSO authentication helpers to reception and encounter workflows. The module can query the NHSO authen status service
from a reception record, populate patient/coverage/location values, and store the returned claim code on both reception and
encounter records.

## Main Components

- `ni.reception` extension Adds `claim_code`, makes `name` non-required, and provides `action_nhso_authen()`.
- `ni.encounter` extension Adds `claim_code` so the selected claim can remain visible after encounter creation.
- Post-init hook `setup_config_param` Seeds a base URL, request headers, and mock payload into `ir.config_parameter`.

## Views

- Reception form: hides the partner block and nationality field, adds an `Authen` button after `identification_id`, and shows
  `claim_code`.
- Encounter form: adds `claim_code` after coverage information.

## Dependencies

- `ni_reception`
- `ni_organization`
- `l10n_th_ni_coverage`

## Notes

- The implementation currently calls the hard-coded `TEST_BASE_URL` constant in Python. The seeded config parameters are not
  used by `action_nhso_authen()`.
- Setting `ir.config_parameter` key `l10n_th_nhso_authen.test_env` enables the built-in dummy response path instead of the HTTP
  response body.
- Claim-code extraction only keeps histories that match the reception date, fixed service code `PG0150001`, and the current
  company `hcode`.
