# Nirun - Timing

Odoo 16.0 module that models timing, dose cadence, and scheduling patterns for clinical use. It supports reusable timing
templates and time-of-day breakdowns that can be shared by medication- and care-related modules.

## Purpose

`ni_timing` provides a structured way to describe when something should happen. The module is designed around clinical timing
concepts such as days of week, named events, templates, and time-of-day fragments so downstream modules can reuse the same
timing vocabulary.

## Main Models

| Model                    | Role                                              |
| ------------------------ | ------------------------------------------------- |
| `ni.timing.dow`          | Day-of-week reference data                        |
| `ni.timing.event`        | Named timing events                               |
| `ni.timing.template`     | Reusable timing template                          |
| `ni.timing.template.tod` | Time-of-day rows on a template                    |
| `ni.timing.timing`       | Concrete timing record                            |
| `ni.timing.timing.tod`   | Time-of-day rows on a timing record               |
| `ni.timing.tod`          | Time-of-day reference model                       |
| `ni.timing.mixin`        | Abstract mixin for timing-aware downstream models |

## Data and Views

- `data/ni.timing.dow.csv`, `data/ni.timing.event.csv`, and `data/ni.timing.template.csv` seed the reference timing vocabulary.
- `data/ir_cron_data.xml` registers scheduled maintenance jobs.
- `views/ni_timing_*` expose the timing dictionaries, templates, and concrete timing records.

## Dependencies

- `ni_coding`

## Verification

- Run `ni_timing/tests/test_ni_timing.py` after changing timing calculations or template behavior.
- Re-check seeded timing dictionaries and template views after changing timing vocabulary or cron behavior.
