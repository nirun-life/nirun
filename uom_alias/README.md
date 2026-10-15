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

- Since Odoo 19 the square-meter and square-foot aliases sit on
  `uom.product_uom_square_meter` and `uom.product_uom_square_foot` (OpenUpgrade renames
  the old `uom.uom_square_*` xmlids). Several aliased units, such as `gal (US)`, are
  archived by default in 19.
- The module does not add any views. Its impact is limited to search behavior and seeded
  alias values.
