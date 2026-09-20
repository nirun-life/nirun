# Grading (`survey_grading`)

## Purpose

Adds named grading bands on top of Odoo survey scoring so completed answers can be classified by score range and shown as badges
in both backend and frontend results. Bands can be scoped to a selected answer, which is what lets one survey carry several sets
of ranges for a maximum score that varies between responses.

## Main Components

- `survey.grade` Stores per-survey grade bands with `low`, `high`, `triggering_answer_ids`, `color_class`, and computed
  `passing_grade`.
- `survey.survey` extension Adds `grade_ids` and `grading_basis`.
- `survey.user_input` extension Adds computed/stored `grade_id`, related `grade_ids`, and related `grade`.
- `survey.question.answer` extension `name_get` prefixes the answer with its question title when the field context sets
  `show_question` (used by the `triggering_answer_ids` widgets), since a survey has many answers sharing the same text.

## Views, Templates, and Security

- Survey form: adds editable grading rows under survey scoring options.
- Survey-user-input tree and form: show the computed grade.
- Frontend completion template, part one and a half: `survey.user_input.grade_scale()` prints the response's value over the top
  of the scale it was graded on (`6 / 6`, or `60 / 100%` under the percentage basis) beside the badge. The ceiling is the
  candidate bands' highest bound, **not** `total_possible_score` — the survey's own maximum overstates the scale whenever
  conditional questions drop out, which is the case `grading_basis = score` exists for.
- Frontend completion template, part two: a **grading reference** table sits between the score block and the statistics charts,
  so a respondent can see the whole scale their badge came from. Its rows are `survey.user_input.grade_reference()` — the bands
  that could still have applied to _this_ response, best first — and not every band of the survey, because answer-scoped sets
  (and the gender/age sets `ni_questionnaire` adds) would otherwise contradict each other on screen. The reached band's row is
  marked with `table-active` plus a titled check icon, never colour alone. A one-band scale renders nothing.
  `survey.user_input.grade_conditions()` supplies the parenthesised hint naming what selected those bands; it is the extension
  seam, so downstream modules add their criteria there rather than xpath'ing into this table.
- Security: grants survey users access to `survey.grade`. The completion page is rendered from sudo records by
  `survey.controllers.main`, so an iterated `grade_ids` is reachable for an anonymous respondent.

## Dependencies

- `survey`

## Grading Basis

`survey.survey.grading_basis` chooses what `low`/`high` are compared against:

- `percentage` (default) `survey.user_input.scoring_percentage`.
- `score` `survey.user_input.scoring_total`, i.e. raw points. Use it when the maximum score varies between responses, because a
  fixed points cutoff is then no longer a fixed percentage.

`survey.user_input._grading_value()` is the single place that resolves this.

## Questionnaires With a Variable Maximum Score

Odoo core already shrinks the maximum: a question that stays hidden because of its conditional display (`is_conditional` /
`triggering_question_id` / `triggering_answer_id`) is removed from `predefined_question_ids` in `_mark_done()`, and
`_compute_scoring_values` builds `total_possible_score` from that field.

Author such a questionnaire like this:

1. Add a gating question whose answer decides which items are administered.
2. Mark the items that may be skipped as conditional on the gating answer.
3. Set `grading_basis` to `score` and create one set of grade bands per gating answer, each with that answer in
   `triggering_answer_ids`.

`triggering_answer_id` is single-valued in Odoo 16.0, so an "any of these answers" gate is expressed with a binary gating
question rather than by scoping the skipped items on several answers.

## Notes

- `triggering_answer_ids` empty means the grade applies to every response. Answer-scoped grades take precedence over unscoped
  ones (`survey.user_input._grade_candidates()`).
- Only one gating question per survey. If bands are scoped on answers of two independent questions, every intersecting band
  becomes a candidate and `_order` silently decides which one wins.
- `_scope_key()` returns the values that make two grades independent. Grades sharing a scope key must have a unique name and
  must not overlap; grades of different scopes may overlap freely. `ni_questionnaire` extends it with gender and age range.
  Because a Many2many cannot take part in a SQL unique index, both rules are Python `@api.constrains`, not `_sql_constraints`.
- Grade ranges must stay within `0.0-100.0` only under the `percentage` basis; under `score` they are bounded only by
  `low <= high`.
- `passing_grade` is derived from the survey's `scoring_success_min` and is always `False` under the `score` basis, since
  `scoring_success_min` is a percentage.
- `grading_basis` is deliberately not `required`. A NOT NULL column on `survey.survey` breaks core survey's own tests, which run
  before this module enters the registry. `score` is the special case everywhere; an empty value reads as `percentage`.

## Verification

`survey_grading/tests/test_survey_grade.py` covers both bases against the same 6-of-10 response, which the two band sets
deliberately grade in opposite directions, plus the grading-reference table: that it lists only candidate bands, marks the
reached one, and names the answer that selected the set.
