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
| `survey.grade`                          | Age- and gender-aware grading extension               |
| `ni.patient.survey_latest`              | Latest completed survey per patient report model      |
| `ni.encounter.survey_latest`            | Latest completed survey per encounter report model    |
| `survey.user_input.line.monthly.report` | Read-only monthly reporting model over survey answers |

## Workflow and Integration

- `models/survey_survey.py` adds subject targeting, observation output settings, and sync logic for grading ranges.
- `models/survey_user_input.py` links responses to patients and encounters, adds database indexes for completed-response
  lookups, and creates `ni.observation` or `ni.observation.sheet` records when a response is completed.
- `models/survey_question.py` and `models/survey_question_group.py` control how individual answers or grouped scores map into
  observation types.
- `models/ni_encounter.py`, `models/ni_patient.py`, and `models/ni_observation_abstract.py` add response counters and launch
  actions from the clinical records.
- `wizard/survey_subject.py` adapts the survey subject wizard for `ni.patient` and `ni.encounter`.

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

- Re-check a full questionnaire flow from patient or encounter launch through completed response creation.
- Confirm completed responses still generate the expected observation or observation sheet records.
- Review latest-response and monthly pivot/report views after any change to answer mapping, grading, or SQL-backed report
  models.
