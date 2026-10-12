# Units of Measure - Alias (`uom_alias`)

## Purpose

Adds alternate search names to units of measure.

## Main Components

- `uom.uom` extension Adds `alias` and sets `_rec_names_search` so name search matches
  either `name` or `alias`.

## Data and Tests

- Seeds aliases for several built-in units such as `sq.m.`, `sq.ft.`, `cu.m.`, `gallon`,
  `cu.in.`, and `cu.ft.`.
- Includes a test that verifies alias search returns the expected UoM record.

## Dependencies

- `uom`

## Notes

- The module does not add any views. Its impact is limited to search behavior and seeded
  alias values.
