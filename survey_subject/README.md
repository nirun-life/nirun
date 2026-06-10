# Survey - Subject (`survey_subject`)

## Purpose

Extends Odoo surveys so answers can be created for an explicit subject record instead of only the current frontend user or
partner.

## Main Components

- `survey.survey` extension Adds required `subject_type` selection and `action_survey_subject_wizard()`.
- `survey.user_input` extension Adds `subject_model`, `subject_id`, computed `subject_ref`, and `subject_name`.
- `survey.subject.wizard` Transient wizard that selects the target subject and opens a survey answer URL for that record.

## Views, Templates, and Security

- Survey form: adds `subject_type`.
- Survey tree/form: adds `Answer Survey` actions that open the subject wizard.
- Survey-user-input tree/form: shows subject reference fields and provides grouped answer actions.
- Frontend templates: adjust the completion page wording and result actions for non-partner subjects.
- Security: grants survey users access to the wizard model.

## Dependencies

- `survey`

## Notes

- `survey.user_input` creates an index on `(subject_model, subject_id)` during `_auto_init()`.
- The wizard currently supports `res.partner` and `res.users` through dedicated subject fields, even though the stored reference
  model field is generic.
