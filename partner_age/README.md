# Partner - Age (`partner_age`)

## Purpose

Adds reusable age tracking to contacts, including birthdate-based age calculation, manual age input fallback, deceased tracking,
age ranges, and daily recomputation jobs.

## Main Components

- `age.mixin` Provides `birthdate`, `deceased_date`, `deceased`, `display_age`, `age`, `age_month`, `age_day`, `age_init`,
  `age_init_date`, and computed `age_range_id`.
- `res.partner` extension Inherits `age.mixin` directly on contacts.
- `res.partner.age.range` Stores named age bands with non-overlapping `age_from` / `age_to` ranges.

## Data, Views, and Automation

- Partner form: adds editable age, birthdate, and deceased-date fields plus hidden internal tracking fields.
- Age-range configuration: adds tree/form views, an action, and a Contacts configuration menu entry.
- Seeds default age ranges from `0-9 Years old` through `100 Years & above`.
- Schedules two daily cron jobs: one recomputes age values, and one recomputes age-range assignments.

## Dependencies

- `base`
- `mail`
- `contacts`

## Notes

- If a record has no birthdate, entering `age` stores the input as `age_init` plus `age_init_date`; subsequent age updates are
  derived from that snapshot.
- The module prevents future birthdates, future deceased dates, deceased dates before birthdate, and negative ages.
- Tests cover partner age calculation, age ranges, and contact integration.
