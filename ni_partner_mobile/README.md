# Partner - Mobile (`ni_partner_mobile`)

## Purpose

Brings back the contact mobile number (`mobile`), which Odoo 19 removed from `base`, as
a field of its own next to `phone`.

## Main Components

- `res.partner` extension Adds `mobile`, formatted like `phone` when it is entered.

## Data, Views, and Security

- Partner form: adds `mobile` under `phone`.
- Partner list: adds `mobile` after `phone` (hidden by default).
- No new model or access rule.

## Verification

- `tests/test_partner_mobile.py`: phone and mobile stay apart, and the phone search
  finds a contact by its mobile.

## Dependencies

- `phone_validation`: formats the number. It also picks up `mobile` as a number field,
  so the "Phone Number" search and SMS use it.

## Upgrade from 18.0

OpenUpgrade 19 keeps the `res_partner.mobile` column, so this module adopts the existing
values. OpenUpgrade also appends the mobile to `phone` ("phone // mobile"); run it with
`upgrade_path/` of this repository as a second `--upgrade-path`, whose
`base/19.0.1.3/post-nirun_partner_mobile.py` puts the original phone back.

## Notes

- License LGPL-3. The field and the formatting are adapted from Odoo 18.0 `base` and
  `phone_validation` (LGPL-3), so Nirun modules under any license can depend on it. The
  OCA `partner_mobile` module provides the same feature under AGPL-3.
