# Grading (`survey_grading`)

## Purpose

Adds named grading bands on top of Odoo survey scoring so completed answers can be classified by percentage range and shown as
badges in both backend and frontend results.

## Main Components

- `survey.grade` Stores per-survey grade bands with `low`, `high`, `color_class`, and computed `passing_grade`.
- `survey.survey` extension Adds `grade_ids`.
- `survey.user_input` extension Adds computed/stored `grade_id`, related `grade_ids`, and related `grade`.

## Views, Templates, and Security

- Survey form: adds editable grading rows under survey scoring options.
- Survey-user-input tree and form: show the computed grade.
- Frontend completion template: renders a colored grade badge when an answer has a matching grade.
- Security: grants survey users access to `survey.grade`.

## Dependencies

- `survey`

## Notes

- Grade ranges must stay within `0.0-100.0`, must not invert `low/high`, and must not overlap other grades on the same survey.
- `passing_grade` is derived from the survey's `scoring_success_min`.
