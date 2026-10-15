# Partner - Titles (`ni_partner_title`)

## Purpose

Brings back contact titles (Mister, Madam, Doctor, ...), which Odoo 19 removed from
`base`. The model keeps its name, `res.partner.title`; the partner field is `title_id`
(`title` up to 18.0), following the Many2one `_id` naming convention.

## Main Components

- `res.partner.title` Title model with translatable `name` and `shortcut`.
- `res.partner` extension Adds `title_id`.

## Data, Views, and Security

- Seeds the five 18.0 titles: Madam, Miss, Mister, Doctor and Professor (`noupdate`).
- Contacts > Configuration > Contact Titles: editable list and form.
- Partner form: adds `title_id` before `lang`, hidden for companies.
- Security: internal users can read titles; contact managers
  (`base.group_partner_manager`) have full access.

## Verification

- `tests/test_partner_title.py`: the default titles and setting a title on a contact.

## Dependencies

- `contacts`: the Contacts configuration menu.

## Upgrade from 18.0

Run OpenUpgrade 19 with `upgrade_path/` of this repository as a second `--upgrade-path`.
Its `base/19.0.1.3/pre-nirun_partner_title.py` hands the existing titles and their
xmlids over to this module before it is installed, and renames the `res_partner.title`
column to `title_id`. No data is copied.

## Notes

- License LGPL-3. The model, views and data are adapted from Odoo 18.0 `base` (LGPL-3),
  so Nirun modules under any license can depend on it. The OCA `partner_title` module
  provides the same feature under AGPL-3.
