# Questionnaire (`ni_questionnaire`)

Odoo 16.0 module that integrates Odoo Survey with Nirun patients, encounters, grading, and observation generation.

## Purpose

`ni_questionnaire` turns surveys into clinical questionnaires. It lets teams assign surveys to patients or encounters, capture
responses in the clinical context, and transform completed answers into structured `ni.observation` records and reporting views.

## Main Models

| Model                                   | Role                                                  |
| --------------------------------------- | ----------------------------------------------------- |
| `survey.survey`                         | Extended with Nirun subject and observation settings  |
| `survey.user_input`                     | Survey response linked to patient and encounter       |
| `survey.user_input.line`                | Response line with stored company context             |
| `survey.question`                       | Extended with observation mapping metadata            |
| `survey.question.group`                 | Groups questions for derived observation calculations |
| `survey.grade`                          | Age-, gender- and interpretation-aware grading        |
| `ni.patient.survey_latest`              | Latest completed survey per patient report model      |
| `ni.encounter.survey_latest`            | Latest completed survey per encounter report model    |
| `survey.user_input.line.monthly.report` | Read-only monthly reporting model over survey answers |

## Workflow and Integration

- `models/survey_survey.py` adds subject targeting, observation output settings, and sync logic for grading ranges.
  `action_sync_observation_range` follows `grading_basis`: under `score` it copies the reference-range bounds unchanged, under
  `percentage` it scales them by the observation type's `max`.
- `models/survey_user_input.py` links responses to patients and encounters, adds database indexes for completed-response
  lookups, and creates `ni.observation` or `ni.observation.sheet` records when a response is completed.
- `models/survey_question.py` and `models/survey_question_group.py` control how individual answers or grouped scores map into
  observation types. `observation_answer_type` and `observation_score_type` are deliberately not `required`: a NOT NULL column
  on `survey.question` or `survey.survey` breaks upstream modules' tests, which run before this module enters the registry.
  `value` and `percentage` are the special cases; an empty value reads as `score` and `raw` respectively.
- A `value`-mapped answer is read by `answer_type`, not by testing each `value_*` field for truthiness. Truthiness rejected a
  legitimate numerical answer of `0` and had no branch for `datetime` at all, both of which blocked survey completion.
- `models/ni_encounter.py`, `models/ni_patient.py`, and `models/ni_observation_abstract.py` add response counters and launch
  actions from the clinical records.
- `wizard/survey_subject.py` adapts the survey subject wizard for `ni.patient` and `ni.encounter`.

### Observations Are Created in `_mark_done()`

`survey.user_input._mark_done()` writes `state = done` first and only then drops the inactive conditional questions from
`predefined_question_ids`, which is what shrinks the maximum behind `scoring_percentage`. Observations are therefore built after
`super()._mark_done()`, not from a `write()` hook — a `write()` hook reads the pre-trim score.

Consequence: closing a live survey session, which writes `state = done` directly (`survey/models/survey_survey.py`), does not
generate observations. Clinical questionnaires are not run as sessions.

### Grade-Driven Interpretation

`survey.grade.interpretation_id` gives the grade a `ni.observation.interpretation`. When a response carries one,
`ni.observation.abstract._interpretation_for()` uses it instead of looking the value up in the observation type's reference
ranges. This is required for questionnaires whose maximum score varies between responses, because
`ni.observation.reference.range` only scopes by age and gender and knows nothing about the survey. Reference ranges remain the
fallback when the grade has no interpretation.

### Grading-Reference Hint

`survey.user_input.grade_conditions()` (from `survey_grading`) is extended to name the patient traits `grade_for()` selected on,
which the completion page prints beside the grading-reference table. Only traits the survey _grades differently by_ are named —
a gender label when any band carries one, an age when the bands fall into more than one age window — otherwise every result page
would carry an age and a gender that had no bearing on the grade.

## Reports, Views, and Security

- `report/ni_patient_survey_latest_*`, `report/ni_encounter_survey_latest_*`, and `report/survey_user_input_line_report_*`
  provide latest-response and monthly analysis models and views.
- `report/ni_patient_observation_views.xml` and `report/ni_encounter_observation_views.xml` surface questionnaire-backed
  observations inside the patient and encounter UIs.
- `views/survey_survey_views.xml`, `views/survey_user_input_views.xml`, `views/ni_patient_views.xml`, and
  `views/ni_encounter_views.xml` expose questionnaire operations across survey and clinical screens.
- `security/res_groups.xml`, `security/ir_rules.xml`, and `security/ir.model.access.csv` define questionnaire-specific access.

## Dependencies

- `ni_patient`
- `survey`
- `survey_subject`
- `survey_grading`
- `ni_observation`

## Verification

- `ni_questionnaire/tests/test_observation_mapping.py` covers the three observation producers (whole-survey score, single
  answer, question group), `grade_for()`, `action_sync_observation_range()`, and the misconfiguration guards.
- `ni_questionnaire/tests/test_variable_max_score.py` covers the variable-maximum path end to end, including a percentage-basis
  case that is the regression guard for creating observations before `_mark_done()` trims.
- `ni_questionnaire/tests/test_completion_page.py` covers the completion page with every extension applied, including the
  patient traits added to the grading-reference hint.
- Re-check a full questionnaire flow from patient or encounter launch through completed response creation.
- Confirm completed responses still generate the expected observation or observation sheet records.
- Review latest-response and monthly pivot/report views after any change to answer mapping, grading, or SQL-backed report
  models.
