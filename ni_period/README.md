# Nirun - Period

Odoo 16.0 utility module that adds reusable datetime range fields for clinical resources. It exists so patient-facing models can
share a consistent `period_start` / `period_end` structure without duplicating field logic.

## Purpose

`ni_period` is a lightweight foundation module. It does not introduce business workflows on its own; instead, it provides the
period mixin that other Nirun modules inherit when they need FHIR-aligned time ranges.

## Main Models

| Model             | Role                                                       |
| ----------------- | ---------------------------------------------------------- |
| `ni.period.mixin` | Abstract mixin that adds period fields to dependent models |

## Dependencies

This module has no runtime dependencies beyond Odoo base.

## Verification

- Re-check dependent modules that inherit `ni.period.mixin` after changing period field or mixin behavior.
