# Patients Bulk Encounter (`ni_patient_bulk`)

Odoo 16.0 module that adds bulk encounter creation for multiple patients and related list or kanban entry points.

## Purpose

`ni_patient_bulk` supports operational workflows where staff need to register the same service date or encounter context for
many patients at once instead of opening each encounter separately.

## Main Models

| Model               | Role                                                        |
| ------------------- | ----------------------------------------------------------- |
| `ni.encounter.bulk` | Wizard for batch encounter creation and optional confirming |

## Workflow and UI

- `wizard/ni_encounter_bulk.py` lets users select a date, encounter class, calendar, and a patient set, while also showing which
  patients already have open encounters on that day.
- `action_create()` creates one `ni.encounter` per selected patient, generates service resources, and optionally confirms the
  new encounters immediately.
- `views/ni_encounter_views.xml` attaches custom JS classes to encounter list and kanban views.
- `static/src/views/bulk_views.esm.js` adds manager-only bulk action buttons that open the wizard from those views.

## Security and Dependencies

- `security/ir.model.access.csv` grants access to the bulk wizard.
- The module depends on `ni_patient`, `ni_practitioner`, `rating`, and `ni_service`.

## Verification

- Re-check bulk encounter creation for mixed patient selections, especially duplicate-prevention on the selected date.
- Confirm generated encounters also create their related service resources and respect the confirm flag.
- Review the custom list and kanban buttons with a manager account after frontend changes.
