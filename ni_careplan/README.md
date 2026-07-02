# Care Plan (`ni_careplan`)

Odoo 16.0 module implementing **HL7 FHIR CarePlan** for the Nirun healthcare platform. Provides structured, goal-driven care
plans linked to patient diagnoses, with guided creation, template-based defaults, and outcome tracking.

## Features

- **5-step creation wizard** — guides clinicians through diagnosis selection, evident observations, goals, interventions
  (services + medications), and final confirmation
- **Template system** — pre-configure goals, service requests, observation types, and medication orders per diagnosis;
  auto-matched when a patient's conditions align
- **Goal tracking** — measurable targets with min/max ranges; achievement status with percentage completion display
- **Interventions** — service requests and medication requests linked to the care plan period
- **Evident observations** — attach relevant patient observations as clinical evidence
- **Custom kanban/list views** — magic-wand "New" button always routes through the wizard; default Odoo "New" button is
  suppressed
- **Calendar view** — plotted by `period_start`/`period_end`, colored by category; sidebar filters on patient (with avatar) and
  category

## Models

| Model                                     | Description                                                                                 |
| ----------------------------------------- | ------------------------------------------------------------------------------------------- |
| `ni.careplan`                             | Core care plan record (inherits `ni.workflow.request.mixin`)                                |
| `ni.careplan.category`                    | Hierarchical category with goal/service/observation defaults                                |
| `ni.careplan.template`                    | Reusable template with condition codes, goals, services, observation types, and medications |
| `ni.careplan.template.service.request`    | Service request prototype in a template                                                     |
| `ni.careplan.template.medication.request` | Medication request prototype (inherits `ni.medication.abstract` for full dosage support)    |

### Wizard (TransientModels)

| Model                                | Description                                        |
| ------------------------------------ | -------------------------------------------------- |
| `ni.careplan.wizard`                 | Main 5-step wizard                                 |
| `ni.careplan.wizard.obs.line`        | Observation evidence selection line                |
| `ni.careplan.wizard.goal.line`       | Goal configuration line with editable target range |
| `ni.careplan.wizard.service.line`    | Service request line                               |
| `ni.careplan.wizard.medication.line` | Medication request line                            |

## Wizard Steps

1. **Diagnosis & Template** — select patient, active conditions, and a matching template (auto-suggested based on condition
   codes)
2. **Observations** — review suggested observation types from condition codes and template; select which to attach as evidence
   (pre-checked when patient data exists)
3. **Goals** — review template goals with pre-computed target ranges; add or remove goals; edit targets
4. **Interventions** — review template service requests and medication orders; add custom lines; deselect unwanted items
5. **Confirm** — set care plan period; choose to confirm immediately (active state) or save as draft

The wizard always opens itself as a dialog. Where the resulting care plan record opens depends on how the wizard was launched:
the careplan action's own "Add care plan" button passes `careplan_form_target=current` in the context so the created record
opens full page; the encounter/patient/condition "New care plan" buttons don't set it, so the record opens in a dialog (the
default).

## Templates

Templates are matched to care plans by **condition code**. When a patient's active diagnoses include a code listed in the
template's `condition_code_ids`, the template is suggested automatically. Templates bundle:

- Goal codes with target types (fixed range or ratio of a patient's latest observation)
- Service request prototypes (name, category, services, timing)
- Medication request prototypes (medication, quantity, dosage schedule)
- Observation types to suggest as evidence

## Care Plan Lifecycle

Follows `ni.workflow.request.mixin`:

```
draft → active → completed
              → on-hold
              → revoked
```

Setting an **achievement** on a care plan automatically transitions it to `completed`.

## Dependencies

- `ni_patient` — patient and encounter models
- `ni_condition` — diagnosis/condition linking
- `ni_observation` — evident observation support
- `ni_service` — service request creation
- `ni_goal` — goal tracking and achievement
- `ni_document_ref` — document attachments
- `ni_medication` — medication request creation

## Configuration

Careplan **Categories** control which observation categories, goal categories, and service categories are relevant to a plan.
Set these on the category record before creating templates.

A category can be scoped to one company (`company_id` set) or left shared (`company_id` unset, visible to every company). Each
company opts into which shared categories it actually wants via `res.company.careplan_category_ids` (Settings > Companies,
Encounter tab). The `category_id` field on care plans, templates, and the wizard is then restricted to: the current company's
own categories, plus whichever shared categories that company has opted into. A shared category's own form shows the reverse
side — `opted_company_ids` — listing which companies have opted into it. `company_id` defaults to the current company for
non-admins and to unset (shared) for `ni_patient.group_admin`.

## Security

Access follows `ni_patient.group_user` — all clinical staff with patient access can create and manage care plans and use the
wizard.

`ni.careplan.template` (and its service/medication request lines) and `ni.careplan.category` are both read-only (use only) for
plain `ni_patient.group_user`. `ni_patient.group_admin` has unrestricted create/write/unlink, including shared
templates/categories. `ni_patient.group_manager` can create/write/unlink templates and categories scoped to their own company
(`company_id` set to one of their companies) but cannot touch shared records (`company_id` unset) or another company's records.
The same own-company, non-shared restriction applies to a manager's edits on a template's service/medication request lines
(checked via the line's `template_id`). The Category menu (under Configuration) is visible to `ni_patient.group_manager` and
above.
