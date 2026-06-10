# Partner - Gender (`partner_gender`)

## Purpose

Adds a gender field to contacts and a default-gender mapping on partner titles so titles can prefill gender automatically.

## Main Components

- `res.partner` extension Adds tracked `gender` selection values `male`, `female`, and `other`.
- `res.partner.title` extension Adds a `gender` default on title records.
- Post-init hook Backfills partner gender for existing contacts that already use the base Mister, Miss, or Madam titles.

## Data and Views

- Loads title data updates from `data/res_partner_tiltle_data.xml`.
- Partner form: shows `gender` after `title` and hides it for companies.
- Partner-title tree and form views: show the title-level gender default for partner managers.

## Dependencies

- `base`

## Notes

- Changing a contact title triggers `onchange` logic that copies the title's configured gender into the contact.
- The post-init hook uses the base Odoo title records to initialize legacy data.
