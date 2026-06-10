# Patient Benefit (`ni_benefit`)

Odoo 16.0 module that adds a reusable benefit or entitlement vocabulary and links those benefit records directly to patients.

## Purpose

`ni_benefit` gives Nirun a lightweight way to classify patient entitlements such as schemes, plans, or internal benefit groups
without hardcoding those values into the patient model.

## Main Models

| Model        | Role                                                 |
| ------------ | ---------------------------------------------------- |
| `ni.benefit` | Hierarchical benefit vocabulary built on `ni.coding` |
| `ni.patient` | Extended with Many2many benefit links and a count    |

## Behavior and Data

- `models/ni_benefit.py` defines `ni.benefit` as a parent-child coding tree and blocks recursive parent assignments.
- `models/ni_patient.py` adds `benefit_ids` and computed `benefit_count` so patient records can carry multiple entitlements.
- `data/ni_benefit_data.xml` seeds the initial benefit reference records shipped with the module.

## Views and Security

- `views/ni_benefit_views.xml` provides list and form maintenance for the benefit catalog.
- `views/ni_benefit_menu.xml` adds the setup menu entry for benefit administration.
- `security/ir.model.access.csv` grants access to the benefit model.

## Dependencies

- `ni_patient`

## Verification

- Re-check patient forms after changes to ensure benefits can be assigned and the computed count stays in sync.
- Confirm benefit hierarchy edits reject recursive parent assignments.
