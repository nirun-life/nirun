# HR Employee Motto (`hr_employee_motto`)

## Purpose

Adds a short free-text motto field to employee records for profile-style personal statements.

## Main Components

- `hr.employee.base` extension Adds `motto = fields.Text(help="Employee's Motto...")`.

## Views

- Employee form: inserts a centered `motto` field with placeholder text before the main notebook in `hr.view_employee_form`.

## Dependencies

- `hr`

## Notes

- This module only changes profile data and the form layout. It does not add security, menus, or reporting behavior.
