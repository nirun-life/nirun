# Base Location Partner Private Form (`base_location_private_form`)

## Purpose

Extends Odoo's private partner form from `base_location` so private/contact records can use the `zip_id` location-completion
widget.

## Views

- Inherits `base.res_partner_view_form_private`.
- Inserts `zip_id` before `city` with `no_open` and `no_create` options.
- Keeps the field readonly for child contact addresses when `type = contact` and `parent_id` is set.

## Dependencies

- `base`
- `base_location`

## Notes

- This module only changes the private partner form layout. It does not add models, fields, or security rules.
