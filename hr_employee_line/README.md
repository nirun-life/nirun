# HR Employee Line ID (`hr_employee_line`)

## Purpose

Adds a LINE contact field to the shared employee base model and exposes it on the employee form.

## Main Components

- `hr.employee.base` extension Adds `line = fields.Char("LINE ID")`.

## Views

- Employee form: inserts `line` immediately after `work_email` on `hr.view_employee_form`.

## Dependencies

- `hr`

## Notes

- The field is added on `hr.employee.base`, so it is available to both employee records and any related models inheriting that
  shared base structure.
