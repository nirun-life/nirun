# Specialty (`ni_specialty`)

Odoo 16.0 module that provides a reusable specialty filter mixin based on practitioner job roles.

## Purpose

`ni_specialty` introduces a small but important access pattern for specialty-aware data. Models that inherit its mixin can be
tagged with one or more specialties and automatically filtered to the current user’s practitioner specialty unless the user has
the configured bypass group.

## Main Models

| Model                | Role                                                        |
| -------------------- | ----------------------------------------------------------- |
| `ni.specialty.mixin` | Abstract mixin that adds specialty tagging and search rules |

## Behavior

- `models/ni_specialty_mixin.py` adds `specialty_ids` as a Many2many to `hr.job`.
- The mixin overrides `_search()` to inject a specialty domain when all of the following are true: the context keeps
  `specialty_test=True`, the current user has an employee job, and the user is not in the bypass group.
- The default bypass group is `base.group_system`, exposed through `_specialty_groups` for downstream overrides.
- Records without a specialty remain visible because the search domain allows either no specialty or the user’s own specialty.

## Dependencies

- `hr`

## Verification

- Re-check search behavior on any model inheriting `ni.specialty.mixin`, especially with users who do and do not have an
  employee job.
- Confirm admin or other bypass-group users still see the full record set.
- Review any downstream override of `_specialty_groups` or `specialty_test` context handling after changes to the mixin.
