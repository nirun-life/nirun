# Partner - Gender (`partner_gender`)

## Purpose

Adds a gender field to contacts and a default-gender mapping on partner titles so titles
can prefill gender automatically.

## Main Components

- `res.partner` extension Adds tracked `gender` selection values `male`, `female`, and
  `other`.
- `res.partner.title` extension (model from `ni_partner_title`) Adds a `gender` default
  on title records.
- Post-init hook Backfills partner gender for existing contacts that already use the
  Mister, Miss, or Madam titles.

## Data and Views

- Loads title data updates from `data/res_partner_tiltle_data.xml`.
- Partner form: shows `gender` before `lang` and hides it for companies.
- Partner-title tree and form views: show the title-level gender default for partner
  managers.

## Verification

- `tests/test_res_partner_gender.py`: title data, the title → gender onchange and the
  post-init backfill.

## Dependencies

- `mail`: `gender` changes are tracked in the chatter.
- `ni_partner_title`: Odoo 19 removed `res.partner.title` and the partner `title` field;
  this module brings them back as `res.partner.title` and `title_id` (LGPL-3).

## Upgrade from 18.0

Run OpenUpgrade 19 with `upgrade_path/` of this repository as a second `--upgrade-path`.
Its `base/19.0.1.3/pre-nirun_partner_title.py` hands the existing titles and their
xmlids and the `res_partner.title` column over to `ni_partner_title` (`title_id`) before
that module is installed. Without it `ni_partner_title` fails to install and contact
titles are lost.

## Notes

- Changing a contact title (`title_id`) triggers `onchange` logic that copies the
  title's configured gender into the contact.
- The post-init hook uses the `ni_partner_title` title records to initialize legacy
  data.
