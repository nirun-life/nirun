# Nirun - Identifier

Odoo 16.0 utility module that adds reusable auto-generated identifiers to clinical resources. It exists so dependent models can
expose stable human-facing identifiers without re-implementing sequence and default logic.

## Purpose

`ni_identifier` is a foundation mixin module. It does not provide end-user workflows on its own; instead, it gives downstream
models a shared `identifier` field pattern that stays consistent across the Nirun clinical stack.

## Main Models

| Model                 | Role                                                               |
| --------------------- | ------------------------------------------------------------------ |
| `ni.identifier.mixin` | Abstract mixin that adds generated identifiers to dependent models |

## Dependencies

This module has no runtime dependencies beyond Odoo base.

## Verification

- Review `ni_identifier/tests/test_models.py` and `ni_identifier/tests/test_ni_identifer_mixin.py` after changing identifier
  defaults or mixin logic.
