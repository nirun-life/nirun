# Coding Specialty (`ni_coding_specialty`)

Odoo 16.0 module that combines the Nirun coding base with the specialty-aware filtering mixin so coded reference data can be
restricted by practitioner specialty.

## Purpose

`ni_coding_specialty` is the bridge between `ni_coding` and `ni_specialty`. It gives coding-style models a standard specialty
tagging pattern so reference vocabularies can be filtered to records relevant to the logged-in practitioner’s job specialty.

## Main Models

| Model                | Role                                                            |
| -------------------- | --------------------------------------------------------------- |
| `ni.coding`          | Reopened to cooperate with specialty-aware descendants          |
| `ni.specialty.mixin` | Abstract mixin for specialty tagging and specialty-based search |

## Behavior

- `models/ni_specialty_mixin.py` adds `specialty_ids` and the specialty-aware `_search()` override used by downstream models.
- `models/ni_coding.py` reopens `ni.coding` so modules can combine Nirun coding behavior with the specialty mixin in a shared
  dependency layer.
- The specialty filter keeps unspecialized records visible and limits specialized records to the current user’s `hr.job` unless
  the bypass group applies.

## Dependencies

- `ni_coding`
- `hr`

## Verification

- Re-check coding searches on downstream models that inherit `ni.specialty.mixin`.
- Confirm specialty filtering can be disabled intentionally with `specialty_test=False` in context where broader searches are
  required.
