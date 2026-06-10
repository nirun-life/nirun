# Care Plan Problem (`ni_careplan_problem`)

Obsolete Odoo 16.0 addon kept in the repository for history. Its manifest marks the module as merged into `ni_careplan` and
`installable=False`.

## Purpose

`ni_careplan_problem` previously linked care plans to related patient observations and observation categories. The
implementation remains in the tree as historical code, but the module is not installable and should not be treated as an active
deployment target.

## Main Models

| Model                  | Role                                                              |
| ---------------------- | ----------------------------------------------------------------- |
| `ni.careplan`          | Extended with observation-based reason selection                  |
| `ni.careplan.category` | Extended with observation categories and observation type filters |

## Historical Behavior

- `models/ni_careplan.py` computes candidate patient observations based on the selected patient and care plan category, then
  preselects problem observations into `observation_ids`.
- `models/ni_careplan_category.py` adds observation categories and optional observation-type narrowing to care plan categories.
- `views/ni_careplan_views.xml` and `views/ni_careplan_category_views.xml` expose that observation-driven care plan linkage.

## Dependencies and Status

- Depends on `ni_careplan` and `ni_observation`.
- The manifest states `installable=False`, so this code is documentary or migration reference material rather than a supported
  module.

## Verification

- If code is ever revived or migrated, compare it against the current `ni_careplan` implementation first instead of reinstalling
  this addon as-is.
