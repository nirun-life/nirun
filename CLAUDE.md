# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git

**Never run `git commit` unless the user explicitly says "commit".** Writing code, fixing bugs, and adding tests do not imply
permission to commit. Always wait for an explicit instruction.

**Do not** add `Co-Authored-By: Claude *` in commit message

## Secrets

**Never hardcode credentials, passwords, tokens, or API keys in any file.** This applies to all files including scripts, skill
files, config, and documentation. Use environment variables instead:

```python
import os
VALUE = os.environ.get("ENV_VAR_NAME", "")
```

`detect-secrets` runs in pre-commit and will block commits containing secrets. If a false positive is flagged, update
`.secrets.baseline` via `detect-secrets scan > .secrets.baseline` — do NOT disable the hook.

## What This Is

**Nirun** is a collection of Odoo 16.0 add-on modules for healthcare providers. It implements clinical data models following the
**HL7 FHIR standard** (Patient, Encounter, Observation, Condition, Procedure, Medication, etc.) on top of Odoo's framework. A
core design priority is that data in the system is **interchangeable with other standards** — field names, value sets, and model
relationships map directly to FHIR resource definitions wherever possible. Thai localization is layered on top (ICD-10-TM,
ICD-9-CM, NHSO, Buddhist calendar, Thai fonts).

When adding new models or fields, prefer names and structures that align with their FHIR counterpart resources and data types.
Value sets (selections, codelists) should use FHIR-defined codes when a standard binding exists.

## Development Setup

**Runtime:** Odoo 16.0, Python 3.10.

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

To run tests for a specific module locally:

```bash
$ODOO_BIN -c odoo.conf -i module_name --test-enable
```

Set `ODOO_BIN` to the path of your local `odoo-bin` script, e.g.:

```bash
# .env or shell profile
export ODOO_BIN=/path/to/odoo-bin          # macOS/Linux
# or on Windows (PowerShell)
$env:ODOO_BIN = "C:\path\to\odoo-bin"
```

Use `-i` (install/update), not `--test-tags` alone — the latter skips the module update step that initialises ORM defaults and
causes schema errors on this setup.

The CI matrix runs against both stock Odoo 16.0 and OCB 16.0 containers. `l10n_th_icd9cm` and `l10n_th_icd10tm` are excluded
from CI because they contain large data files.

## Translations

Thai translations live in `<module>/i18n/th.po`. **Always regenerate the `.po` file before editing translations** whenever new
strings are added to a module (new fields, view labels, filter strings, etc.). Use the export script in `.tools/`:

```bash
ODOO_MODULE=<module_name> $ODOO_BIN shell -c odoo.conf --no-http < .tools/export_po.py
```

- (Windows) Run via the Bash tool (not PowerShell) — `VAR=value cmd` inline env var syntax requires bash
- `ODOO_MODULE` defaults to `ni_patient`; `ODOO_LANG` defaults to `th_TH`
- The script resolves the output path via Odoo's addon registry — no hardcoded paths, works on any machine
- After export, open the `.po` file and fill in the empty `msgstr ""` entries

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
timeline. **`ni.workflow.line`** is a read-only `_auto=False` SQL UNION view over both tables, used to display events and
requests together in a single timeline list/kanban.

### Key Supporting Modules

- **`ni_coding`** — base for clinical coding systems (ICD, SNOMED, etc.). `l10n_th_icd10tm` and `l10n_th_icd9cm` provide
  Thai-specific code data.
- **`ni_identifier`** / `ni_identifier.mixin` — adds an auto-generated `identifier` field to models.
- **`ni_period`** / `ni_period.mixin` — adds `period_start` / `period_end` datetime range fields.
- **`ni_timing`** — models dosing/scheduling timing (days of week, events).

### Testing Pattern

Tests use `odoo.tests.TransactionCase` with a `common.py` that creates users with appropriate security groups. Use
`odoo.tests.Form` for UI-level field interaction testing.

# ODOX framework

- ODOX is a self-documenting documentation contract for Odoo repositories.
- Agents must follow this file before editing code or durable documentation.

## Purpose

- Keep Odoo repositories understandable at the repo level and at the module level.
- Make module `README.md` files the primary local contract for both humans and AI agents.
- Keep `AGENTS.md` focused on agent-specific workflow, routing, and hazards that do not belong in a human-facing README.

## Core Contract

- The root `AGENTS.md` is mandatory and owns repo-wide workflow, indexing, and documentation maintenance rules.
- The default durable boundary is the Odoo module or addon, not every nested folder.
- Each module should have one primary `README.md` that reflects the current code in that module.
- Module `AGENTS.md` files are optional and additive. They may refine local agent behavior but must not duplicate or contradict
  the module README or this root contract.
- When code and documentation disagree, treat the current code as the source of truth and bring the documentation back into
  sync.

## Read Before Editing

1. Read the root `AGENTS.md`.
2. Identify whether the work is repo-wide or contained within one or more Odoo modules.
3. For repo-wide work, read the root `README.md` and any directly relevant local docs.
4. For module work, read that module's `README.md` first.
5. If the module also has an `AGENTS.md`, read it after the module README and before editing.
6. If multiple modules are affected, repeat the read path for each affected module.
7. Use the nearest applicable module README as the local shared contract and the nearest applicable `AGENTS.md` as the local
   agent supplement.

Do not rely on memory. Re-read the applicable ODOX chain in the current session before editing.

## Update After Editing

Every meaningful change requires an ODOX pass before the task is done.

Update the closest owning documentation when a change affects:

- purpose, scope, ownership, or responsibilities
- durable structure, models, views, security, workflows, dependencies, or extension points
- required inputs, outputs, permissions, constraints, side effects, or artifacts
- verification commands, test entrypoints, or operational checks
- user preferences about behavior, communication, process, organization, or quality
- documentation structure, including `README.md` or `AGENTS.md` creation, deletion, move, rename, or index contents

Update the root docs when repo-wide structure or module inventory changes. Update a module README when local code behavior or
structure changes. Update a module `AGENTS.md` only when agent-specific local instructions change.

## Module Documentation Rules

- Default to `README.md` as the primary contract inside each Odoo module.
- Keep module READMEs operational, technical, and aligned with current code. Avoid marketing copy as the main content.
- A good module README usually covers:
  - purpose and business scope
  - main models, wizards, views, security areas, and data files
  - integration points, dependencies, and extension seams
  - verification or test entrypoints when they exist
  - human-relevant hazards or invariants
- Do not repeat repo-wide setup, install, or generic test boilerplate in module READMEs when the root `AGENTS.md` or root
  `README.md` already owns that workflow.
- Keep module verification sections focused on module-specific entrypoints, special checks, dependent test files, or notable
  validation scope. If a module has no special verification guidance beyond the shared repo workflow, omit the section instead
  of restating boilerplate.
- Use 300 lines as a soft readability threshold for module READMEs.
- If a module README grows much beyond 300 lines, review whether to split module responsibilities, trim stale prose, or move
  agent-only detail into an optional module `AGENTS.md`.
- If a module cannot stay understandable near that threshold, treat it as a signal that the module boundary or documentation
  structure needs reconsideration.
- Prefer a compact maintainer-reference layout for module READMEs but not limit to:
  - module overview and owned scope
  - core models
  - a short architecture or integration map
  - menu map, when the module exposes its own menu
  - main view types plus the views the module modifies and why
  - security summary and permission matrix
  - dependency and extension map only when it adds information not already covered above
  - common pitfalls or invariants that are easy to break
- If two sections repeat the same relationship or workflow, merge them into one integration-oriented section instead of keeping
  both.
- If a module has no standalone menu, say so explicitly rather than inventing a menu tree.
- Document only the inherited views and model extensions that the module actually changes; do not restate generic Odoo
  conventions that already apply everywhere.

## Optional Module AGENTS.md Rules

- Create a module `AGENTS.md` only when at least one of these is true:
  - the module has agent-specific edit hazards that do not belong in the README
  - the module has a non-obvious maintenance workflow or generated-artifact rule
  - the module has local constraints that would clutter the human-facing README
  - the module has multiple subareas that need explicit agent routing
- Keep module `AGENTS.md` files short and supplemental.
- Do not restate the full README in `AGENTS.md`.
- No deeper child `AGENTS.md` files should be created inside a module unless the user explicitly wants an exception.

## Style

- Keep docs concise, current, and operational.
- Prefer durable facts over intentions or roadmap language.
- Put broad workflow rules in the root `AGENTS.md`.
- Put module behavior and code-facing context in the module `README.md`.
- Put agent-only constraints in optional module `AGENTS.md`.
- Delete stale or contradictory text immediately instead of explaining history.

## Verification

- Before finishing meaningful work in a module, verify that the module README still matches the current code.
- Before finishing repo-wide documentation changes, verify that root guidance, module rules, and indexes agree with each other.
- When an existing automated check exists, run it. When none exists, perform a manual consistency review of the touched docs and
  code.

## User Preferences

- Prefer module-level `README.md` as the main shared contract for humans and agents.
- Keep the root model hybrid: root `AGENTS.md` for repo-wide agent workflow, root `README.md` for human-facing overview.
- Treat 300 lines as a soft README review threshold, not a hard cap.
- Keep module `AGENTS.md` rare and justified by real agent-only needs.

## Child DOX Index

- Root scope: this file currently owns the entire repository.
- Human-facing root overview: [README.md](C:\Users\pirui\Workspace\piruin\odox\README.md)
- No child `AGENTS.md` files exist yet in this starter repository.
- Expected adopter structure:
  - repo root: root `AGENTS.md` plus root `README.md`
  - each Odoo module: module `README.md`
  - exceptional modules only: supplemental module `AGENTS.md`
