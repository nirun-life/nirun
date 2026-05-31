# Flag (`ni_flag`)

Odoo 16.0 module implementing the **HL7 FHIR R4 Flag resource** for the Nirun healthcare platform. Records prospective warnings
and safety notes about a patient — visible at a glance on both the patient and encounter forms without any extra navigation.

## After Install

### Patient form

A row of colored tag badges appears directly below the patient name, one badge per active flag.

- **Click `+`** — opens a dropdown to pick a Flag Code; saving creates a new active `ni.flag` record
- **Click `×`** on a badge — deactivates the flag and sets its end date; the badge disappears immediately
- No page navigation required

### Encounter form

The same editable flag tag area appears below the encounter title. Flags added here are scoped to the specific encounter
(`encounter_id` is set on the `ni.flag` record). Patient-level flags (no `encounter_id`) are visible on the patient form.

### Patient kanban

Active flag tags are rendered inline on each patient card, visible without opening the patient.

### Patient search / filters

| Filter              | Behaviour                                        |
| ------------------- | ------------------------------------------------ |
| Has Active Flag     | Filters patients with at least one `active` flag |
| Flag (search field) | Free-text search matched against flag code name  |

### Flag Codes config

Under **Configuration → Flags → Flag Codes**, each code shows an **Active Patients** stat button. Clicking it opens a filtered
patient list — all patients currently carrying that flag.

### Flags report

A **Flags** entry under the Patient root menu opens the flag list with tree, pivot, and graph views. The pivot view groups by
flag code (rows), useful for reviewing flag distribution across patients.

## Flag Lifecycle

```
active ──────────────────────────► inactive
  ▲     (action_inactive / remove tag)    │
  └─── (action_active / re-add tag)  ─────┘
       (period_end set on deactivation,
        cleared on re-activation)

active / inactive ──► entered-in-error
```

- `period_start` — set to creation time automatically
- `period_end` — set to the moment the flag is deactivated
- An hourly cron removes accidental flags: any `inactive` flag where `period_end − period_start < 60 s` is deleted

## Flag Codes and Categories

Seeded on install:

| Code  | Name                  | Category            |
| ----- | --------------------- | ------------------- |
| DNR   | Do Not Resuscitate    | Clinical (CL)       |
| LATEX | Latex Allergy         | Clinical (CL)       |
| FALL  | Fall Risk             | Behavioral (BH)     |
| INTRP | Interpreter Required  | Administrative (AD) |
| ISOL  | Isolation Precautions | Clinical (CL)       |

Categories follow the [FHIR Flag category value set](http://hl7.org/fhir/ValueSet/flag-category): `CL` Clinical · `AD`
Administrative · `BH` Behavioral · `RS` Research.

Add custom codes under **Configuration → Flags → Flag Codes**. Choose a color; the color is used for the badge on the patient
form and kanban card.

## Configuration

No required configuration. Optional:

- **Flag Codes** — add organization-specific codes (group `ni_patient.group_admin`)
- **Flag Categories** — extend the four FHIR defaults (group `ni_patient.group_admin`)

## Dependencies

- `ni_patient` — patient, encounter, and security groups
- `ni_period` — `period_start` / `period_end` fields
- `ni_identifier` — auto-generated `FLG-YYYY-NNNNN` identifier
- `ni_coding` — base coding system for Flag Code and Category models
