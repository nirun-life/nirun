# Partner - Title Unique (`partner_title_unique`)

## Purpose

Prevents duplicate partner-title names.

## Main Components

- `res.partner.title` extension Adds SQL constraint `name_unique` on `name`.

## Dependencies

- `base`

## Notes

- The module has no views or data files. Its only behavior is the uniqueness constraint and validation message.
