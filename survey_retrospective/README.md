# Survey - Retrospective (`survey_retrospective`)

## Purpose

Adds retrospective survey entry support so privileged users can record an answer as if it were created in the past.

## Main Components

- `survey.user_input` extension Adds boolean `retrospective`.
- `survey.subject.wizard` extension Adds `retrospective` and `survey_date`, forwards the retrospective flag into answer
  creation, and rewrites `survey_user_input.create_date` when a past survey date is supplied.

## Views

- Survey-user-input tree and form: show the `retrospective` flag.
- Survey subject wizard: adds hidden/internal retrospective controls for `base.group_no_one`.

## Dependencies

- `survey_subject`

## Notes

- Retrospective mode requires `survey_date`, and the date must be strictly earlier than the current time.
- The module updates `create_date` through direct SQL after answer creation.
