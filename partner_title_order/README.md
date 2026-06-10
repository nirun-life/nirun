# Partner - Title Order (`partner_title_order`)

## Purpose

Adds explicit sequence ordering to partner titles.

## Main Components

- `res.partner.title` extension Adds required integer `sequence` and changes `_order` to `sequence`.
- Default sequencing New titles default to the next sequence after the current highest record.

## Views

- Partner-title tree: adds a drag handle for `sequence` before `name`.

## Dependencies

- `base`

## Notes

- This module changes ordering behavior but does not add new menus or security rules.
