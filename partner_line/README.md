# Partner Line ID (`partner_line`)

## Purpose

Adds a LINE contact identifier to partner records.

## Main Components

- `res.partner` extension Adds `line = fields.Char("LINE ID")`.
- SQL constraint Enforces uniqueness of non-null LINE IDs through `line_uniq`.

## Views

- Partner form: inserts `line` after `website`.

## Dependencies

- `hr`

## Notes

- The dependency is `hr`, but the module behavior itself is limited to `res.partner`.
