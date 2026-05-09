# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

**Nirun** is a collection of Odoo 16.0 add-on modules for healthcare providers. It implements clinical data models following the
**HL7 FHIR standard** (Patient, Encounter, Observation, Condition, Procedure, Medication, etc.) on top of Odoo's framework. A
core design priority is that data in the system is **interchangeable with other standards** — field names, value sets, and model
relationships map directly to FHIR resource definitions wherever possible. Thai localization is layered on top (ICD-10-TM,
ICD-9-CM, NHSO, Buddhist calendar, Thai fonts).

When adding new models or fields, prefer names and structures that align with their FHIR counterpart resources and data types.
Value sets (selections, codelists) should use FHIR-defined codes when a standard binding exists.

## Development Setup

**Local (Windows):** Odoo runs at `http://localhost:16669`. Config is in `odoo.conf`. The `addons_path` includes both this repo
and a `nirun-3rd-party` sibling repo.

**Docker:** Uses `odoo-docker.conf`. Build with `Dockerfile` (based on `nirun/odoo:latest`).

Install Python dependencies:

```
pip install -r requirements.txt
pip install -r test-requirements.txt
```

Install pre-commit hooks:

```
pre-commit install
```

## Running Tests

Tests run via the OCA CI toolchain (used in GitHub Actions):

```
oca_install_addons
oca_init_test_database
oca_run_tests
```

To run tests for a specific module locally with Odoo:

```
python odoo-bin -c odoo.conf --test-enable --test-tags /module_name -d <database>
```

The CI matrix runs against both stock Odoo 16.0 and OCB 16.0 containers. `l10n_th_icd9cm` and `l10n_th_icd10tm` are excluded
from CI because they contain large data files.

## Code Style

All formatting is enforced via pre-commit. Run manually with `pre-commit run --all-files`.

- **Python:** black (line length 88), autoflake, isort, flake8 (max line 120), pylint-odoo
- **XML:** prettier with `--print-width=120`
- **JavaScript:** eslint
- isort import order: `FUTURE, STDLIB, THIRDPARTY, ODOO, ODOO_ADDONS, FIRSTPARTY, LOCALFOLDER`
- All files must have LF line endings and no trailing whitespace

Manifests require: `license` key (LGPL-3 or OPL-1), `author` must include "NSTDA".

All new files must include a copyright header at the top:

```python
#  Copyright (c) <year> NSTDA
```

## Architecture

### Module Naming Conventions

| Prefix      | Purpose                            |
| ----------- | ---------------------------------- |
| `ni_*`      | Core clinical/healthcare modules   |
| `l10n_th_*` | Thai localization modules          |
| `partner_*` | Extensions to `res.partner`        |
| `survey_*`  | Extensions to Odoo's survey module |
| `web_*`     | Frontend/UI customizations         |

### Core Data Model Hierarchy

**`ni.patient`** — central model, uses `_inherits = {"res.partner": "partner_id"}`. Tracks demographics, encounters, and
presence state (draft/planned/in-progress/finished/deceased).

**`ni.encounter`** — a patient visit/admission, uses `_inherits = {"ni.patient": "patient_id"}`. The active encounter is
referenced throughout all clinical resources.

**`ni.patient.res`** (abstract mixin) — base for all patient-linked resources. Provides `patient_id` and `encounter_id` fields,
company-scoped access, and a shared DB index on `(company_id, patient_id, encounter_id)`. All clinical models (observation,
condition, procedure, medication, allergy, etc.) inherit this.

### Workflow Pattern

Two abstract mixins drive state-machine behavior across clinical models:

- **`ni.workflow.event.mixin`** — for completed events (observations, procedures). States:
  `preparation → in-progress → completed / not-done / abort / suspended`.
- **`ni.workflow.request.mixin`** — for ordered/requested items (medication requests, care plans). States:
  `draft → active → completed / on-hold / revoked`.

Both write a mirror record into `ni.workflow.event` / `ni.workflow.request` on every create/write, creating a unified patient
timeline.

### Key Supporting Modules

- **`ni_coding`** — base for clinical coding systems (ICD, SNOMED, etc.). `l10n_th_icd10tm` and `l10n_th_icd9cm` provide
  Thai-specific code data.
- **`ni_identifier`** / `ni_identifier.mixin` — adds an auto-generated `identifier` field to models.
- **`ni_period`** / `ni_period.mixin` — adds `period_start` / `period_end` datetime range fields.
- **`ni_timing`** — models dosing/scheduling timing (days of week, events).

### Testing Pattern

Tests use `odoo.tests.TransactionCase` with a `common.py` that creates users with appropriate security groups. Use
`odoo.tests.Form` for UI-level field interaction testing.
