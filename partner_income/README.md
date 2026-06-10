# Partner - Income (`partner_income`)

## Purpose

Adds income tracking to contacts using monetary values paired with working-time units.

## Main Components

- `res.partner` extension Adds `income`, `income_currency_id`, `income_uom`, and helper `income_uom_categ`.
- Default income unit selection Chooses the reference unit from Odoo's working-time UoM category.

## Data and Views

- Seeds extra working-time units: `Weeks`, `Months`, and `Years`.
- Partner form: adds `income` plus `/ income_uom` on the main contact form and nested child-contact form sections.
- The income unit field becomes required when income is set to `>= 1`.

## Dependencies

- `base`
- `uom`

## Notes

- The UI hides income fields for invoice, delivery, other, and private address records.
