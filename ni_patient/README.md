# Patient (`ni_patient`)

Odoo 18.0 module that provides the core patient and encounter model for Nirun. It
anchors the clinical data hierarchy, patient/encounter workflow state, and shared
timeline records used by the rest of the healthcare modules.

## Purpose

`ni_patient` is the central clinical module in the repository. It owns the patient
record, encounter lifecycle, and the read-only workflow timeline that combines events
and requests into a single patient history.

## Main Models

| Model                                              | Role                                                                |
| -------------------------------------------------- | ------------------------------------------------------------------- |
| `ni.patient`                                       | Central patient record, `_inherits` `res.partner`                   |
| `ni.encounter`                                     | Patient visit/admission, `_inherits` `ni.patient`                   |
| `ni.patient.res`                                   | Abstract mixin for patient-linked clinical records                  |
| `ni.workflow`                                      | Shared workflow base used by event and request records              |
| `ni.workflow.event`                                | Stored timeline mirror for completed events                         |
| `ni.workflow.request`                              | Stored timeline mirror for requested items                          |
| `ni.workflow.line`                                 | Read-only union view over events and requests                       |
| `ni.location` and related encounter support models | Location, class, participant, admit, discharge, and reason metadata |

## Workflow and Views

- `ni.workflow.event.mixin` and `ni.workflow.request.mixin` power the state transitions
  used by downstream clinical modules.
- `ni.encounter` does not inherit the event mixin (its own `state` selection is
  incompatible with the mixin's). Instead, `Encounter._log_workflow_event()`
  (`models/ni_encounter.py`) creates a new `ni.workflow.event` row on every state
  transition (`write()` when `state` changes), so encounter start/discharge/cancel/etc.
  show up in the patient timeline alongside other clinical events.
- `views/ni_workflow_event_views.xml`, `views/ni_workflow_request_views.xml`, and
  `views/ni_workflow_line_views.xml` expose the timeline and state history.
- The encounter form's action menu includes "Workflow Timeline"
  (`Encounter.action_encounter_workflow_timeline()`, bound via
  `ni_encounter_action_server_workflow_timeline` in `views/ni_encounter_views.xml`),
  which opens `ni_workflow_line_action` filtered to that encounter's `ni.workflow.line`
  rows — the same pattern used by the "Location History" and "Participant History"
  action-menu entries.
- `views/ni_patient_views.xml`, `views/ni_encounter_views.xml`, and the related support
  views define the core patient and encounter UI.
- Portal templates in `views/ni_patient_portal.xml` and
  `views/ni_patient_portal_templates.xml` expose patient-facing entry points.

## Display Names and Search

- `ni.patient` sets `_rec_name = "name"`: patients display by name, not by the
  identifier (HN) that `ni.identifier.mixin` would use. `_compute_display_name` (via the
  `_name_get()` extension seam, extended by `ni_observation`) adds details for the
  context keys `show_identifier`, `show_identification_id`, `show_gender_age` and
  `show_age`. Name search covers `name`, `identifier` and `identification_id`
  (`_rec_names_search`).
- `ni.encounter` display name honours `show_class`, `show_patient`/`show_patient_name`,
  `show_state`, `show_location` and `show_period`; name search covers the encounter
  number and the patient.
- `ni.location` display name honours `location_display="short"`, `show_parent` and
  `show_alias`; `full_name` is the parent path with alias.
- `res.partner` search by display name (`_search_display_name`) also matches the exact
  phone, mobile or identification number, on top of the core partner search.

## Addresses

- Patient and encounter "other addresses" are `res.partner` records of type `other` with
  `ref` set to the patient identifier, edited in the compact form
  `res_partner_view_form_address`. Up to 16.0 they were `private` partners, a type Odoo
  17 removed.
- Upgrade from 16.0: `migrations/17.0.1.0.0/post-migration.py` restores those addresses
  from OpenUpgrade's `ou_res_partner_private` copy (OpenUpgrade masks private addresses)
  and sets them to `other`.

## Computed Fields

- Stored and non-stored computed fields use separate compute methods (Odoo 18 warns
  otherwise): e.g. `ni.patient.encounter_count`/`encounter_start`,
  `res.partner.patient_id`, `ni.location.encounter_active_*`.
- `ni.encounter.display_age` is the age at the encounter start (`_compute_display_age`
  overrides the `partner_age` one).

## Encounter Locking

- Encounter fields are read-only in the form once the encounter is finished, cancelled
  or entered in error, and the patient, number and start are editable only in draft.
  Since 17.0 this lives in `views/ni_encounter_views.xml` (`readonly="state ..."`), not
  in field `states=`. Forms of downstream modules that edit `ni.workflow` `intent`/
  `priority` must add their own `readonly` expression for completed/revoked requests.

## Frontend View Registrations

- `static/src/views/form_view.esm.js` and `static/src/views/list_view.esm.js` register
  the `ni_patient_form` and `ni_patient_list` view types; the base patient form and tree
  in `views/ni_patient_views.xml` carry the matching `js_class`.
- Both controllers replace the standard Archive action menu item through the shared
  `static/src/views/archive_patient_hook.esm.js`, which opens
  `ni.patient.archive.wizard` with `default_patient_ids` (one id from the form, the
  whole selection from the list).
- Invariant: archiving a patient must go through that wizard — it is the only path that
  records state reason, date, and note. A plain `write({"active": False})` bypasses it
  and loses that data.
- `PatientListController` is an extension seam imported by downstream repositories
  (since 17.0 from `@ni_patient/views/list_view.esm`); renaming it is a breaking change
  outside this module. The controllers override `getStaticActionMenuItems()`.

## Security and Support Files

- `security/ni_patient_group.xml` defines the patient access group.
- `security/ni_patient_rules.xml` constrains record access.
- `security/ir.model.access.csv` grants model-level permissions.
- `data/ir_sequence_data.xml` and the other `data/*.xml` files seed encounter classes,
  discharge data, participant types, and state reasons.
- `wizard/ni_encounter_discharge_wizard_views.xml` and
  `wizard/ni_patient_archive_wizard_views.xml` support guided encounter and archive
  actions.

## Dependencies

- `ni_coding`
- `ni_identifier`
- `ni_period`
- `hr`
- `mail`
- `partner_age`
- `partner_gender`
- `partner_religion`
- `portal`

## Verification

- `tests/test_ni_patient_display_name.py` (D1), `tests/test_ni_patient_address.py`
  (address type) and `tests/test_ni_coding_default_views.py` (ni_coding default views on
  every coding model).
- Review `ni_patient/tests/test_ni_patient.py` and
  `ni_patient/tests/test_ni_workflow.py` after any workflow, security, or portal change.
- Re-check patient, encounter, workflow timeline, and portal flows after structural
  changes to the core models.
