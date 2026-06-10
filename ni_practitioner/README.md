# Practitioner (`ni_practitioner`)

Odoo 16.0 module that adapts Odoo HR records for clinical practitioner use in Nirun. It adds practitioner-facing resume,
license, specialty, and encounter integration so staff records can support clinical workflows instead of generic HR data only.

## Purpose

`ni_practitioner` bridges HR and clinical data. It extends employee and resume models with coding-based categories and
practitioner identifiers, then links those staff records into encounter workflows where clinician context matters.

## Main Models

| Model                            | Role                                                            |
| -------------------------------- | --------------------------------------------------------------- |
| `hr.employee` extension          | Adds practitioner license fields and default license resolution |
| `hr.employee.public` extension   | Mirrors practitioner-facing fields for public employee access   |
| `hr.employee.category` extension | Coding-backed employee category and specialty vocabulary        |
| `hr.resume.line` extension       | Practitioner resume and credential records                      |
| `hr.resume.line.code`            | Resume credential terminology dictionary                        |
| `res.users` extension            | User-to-practitioner linkage support                            |

## Data, Views, and Assets

- `data/hr_employee_category_data.xml`, `data/hr_resume_line_type_data.xml`, and `data/hr_resume_line_code_data.xml` seed
  practitioner vocabularies and resume structures.
- `views/hr_employee_view.xml`, `views/hr_resume_line_views.xml`, `views/hr_resume_line_code_views.xml`, and
  `views/hr_employee_category_views.xml` provide the main practitioner UI.
- `views/ni_encounter_view.xml` links practitioner information into encounter workflows.
- `static/src/xml/resume_templates.xml` customizes backend resume rendering.

## Operational Notes and Dependencies

- `hook.py` defines a `pre_init_hook` that adds the `active` column to `hr_employee_category` before Odoo model initialization.
- `security/ir.model.access.csv` grants model permissions.
- The module depends on `hr_skills` and `ni_patient`.

## Verification

- Re-check installation or migration paths that touch `hr_employee_category`, because the module relies on the pre-init hook to
  prepare that table.
- Re-check employee license selection, resume-line coding, and encounter practitioner displays after changing HR model
  extensions or resume templates.
