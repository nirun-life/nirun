# HR Employee Religion (`hr_employee_religion`)

## Purpose

Adds religion tracking to employee records by linking employees to the shared `res.religion` master data model.

## Main Components

- `hr.employee.base` extension Adds `religion_id = fields.Many2one("res.religion")`.

## Views

- Employee form: inserts `religion_id` before `gender` on `hr.view_employee_form`.

## Dependencies

- `hr`
- `partner_religion`

## Notes

- The module relies on `partner_religion` to provide the `res.religion` model and any shared master data or UI behavior around
  that relation.
