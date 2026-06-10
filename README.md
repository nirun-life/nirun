# Nirun
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![test](https://github.com/nirun-life/nirun/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/nirun-life/nirun/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](https://hub.docker.com/r/nirun/nirun/)

> **Nirun** means **"Eternity"** in Thai.

Nirun is a collection of Odoo 16.0 add-on modules for healthcare providers, built around **[HL7 FHIR](https://hl7.org/fhir/R4/)** data models (Patient, Encounter, Observation, Condition, Procedure, Medication, etc.). Data is designed to be interchangeable with other FHIR-compliant systems. Thai localization (ICD-10-TM, ICD-9-CM, NHSO, Buddhist calendar) is layered on top.

## Who Is This For?

- Hospitals, clinics, nursing homes and any organization working on healthcare domain
- Developers building healthcare information system

## Requirements

- Odoo 16.0 (Community or Enterprise)
- Python 3.10
- PostgreSQL 14+

## Quick Start

The easiest way is Docker — image is published on [Docker Hub](https://hub.docker.com/r/nirun/nirun/):

```bash
docker pull nirun/nirun
docker run -p 8069:8069 nirun/nirun
```

Open `http://localhost:8069` and install modules via the **Apps** menu.

## Architecture

All clinical models inherit from a shared hierarchy:

```
res.partner
└── ni.patient          (_inherits res.partner)
    └── ni.encounter    (_inherits ni.patient)
        └── ni.patient.res  (abstract mixin — base for all clinical resources)
            ├── ni.observation
            ├── ni.condition
            ├── ni.procedure
            ├── ni.medication.request
            └── ni.careplan
```

State-machine behavior is provided by two abstract mixins:
- **`ni.workflow.event.mixin`** — completed events (observations, procedures): `preparation → in-progress → completed / not-done`
- **`ni.workflow.request.mixin`** — ordered items (medication requests, care plans): `draft → active → completed / on-hold / revoked`

## Module Groups

| Group | Key Modules | Purpose |
| --- | --- | --- |
| **Core Clinical** | `ni_patient`, `ni_encounter`, `ni_observation`, `ni_condition`, `ni_procedure` | FHIR base resources |
| **Care Management** | `ni_careplan`, `ni_goal`, `ni_service` | Care planning & goal tracking |
| **Medication** | `ni_medication`, `ni_medication_suggest` | Prescribing & suggestions |
| **Scheduling** | `ni_appointment`, `ni_reception`, `ni_timing` | Booking & reception |
| **Coding Systems** | `ni_coding`, `l10n_th_icd10tm`, `l10n_th_icd9cm` | Medical classifications |
| **Thai Localization** | `l10n_th_*` | NHSO, coverage, fonts, Buddhist calendar |
| **Partner Extensions** | `partner_*` | Demographic fields on `res.partner` |
| **UI Enhancements** | `web_*` | Frontend customizations |
| **Utilities** | `ni_identifier`, `ni_period`, `uom_alias` | Shared mixins & helpers |

## License

Modules are licensed under **LGPL-3** or **OPL-1** — see each module's `__manifest__.py` for the specific license.

## Security

Security issues in Nirun code should be reported privately as described in [SECURITY.md](SECURITY.md).

## Maintainers

- [Piruin Panichphol](https://github.com/piruin)
