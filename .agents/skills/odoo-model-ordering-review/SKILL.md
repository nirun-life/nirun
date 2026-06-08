---
name: odoo-model-ordering-review
description:
  Use when creating, editing, or reviewing Odoo model Python files, especially before claiming model work is complete or when
  reorganizing model methods and fields.
---

# Odoo Model Ordering Review

Use this as a finishing pass after changing Odoo model files.

Reference:

- Odoo coding guidelines:
  `https://www.odoo.com/documentation/18.0/contributing/development/coding_guidelines.html#symbols-and-conventions`

## Goal

Keep model files ordered predictably so fields, compute helpers, actions, and business methods are easy to scan and consistent
across modules.

## Required Order

In each model class, keep this order:

1. Private attributes
2. Default methods and `default_get`
3. Field declarations
4. Compute, inverse, and search methods in the same order as their fields
5. Selection helper methods
6. Constraint and onchange methods
7. CRUD overrides
8. Action methods
9. Other business methods

Private attributes include items such as:

- `_name`
- `_description`
- `_inherit`
- `_order`
- `_sql_constraints`
- other `_...` class attributes

## Review Pass

For every changed model file:

1. Scan class structure before editing for behavior.
2. Move class attributes to the top if they appear below fields or methods.
3. Keep each field's compute, inverse, and search helpers close together and in the same field order as declarations.
4. Move action methods together under the CRUD section.
5. Move helper methods that are not actions below the action section.
6. Preserve behavior exactly while reordering.

## Practical Rules

- Do not mix action methods with compute/search helpers.
- Do not leave `_sql_constraints` below field declarations.
- If a helper only exists for one field, keep it near that field's other helper methods.
- If reordering reveals an oversized class, note it, but do not split files unless the task requires it.
- After reordering, run syntax checks and the module's normal tests before claiming success.

## Completion Checklist

- Model classes follow the required section order.
- Compute/inverse/search helpers match field declaration order.
- Action methods are grouped together.
- Non-action business helpers come last.
- Verification has been run after the reorder.
