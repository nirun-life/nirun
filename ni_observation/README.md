# Observation (`ni_observation`)

Odoo 16.0 module that implements FHIR-style clinical observations for Nirun. It covers measurements, laboratory values, vital
signs, interpretation logic, and the supporting reference data needed to store and display observations consistently.

## Purpose

`ni_observation` is the observation layer for the patient timeline. It builds on `ni_patient` so clinicians can record
structured measurements with units, interpretation, categories, and reusable observation types instead of ad hoc text fields.

## Main Models

| Model                             | Role                                        |
| --------------------------------- | ------------------------------------------- |
| `ni.observation`                  | Core observation record                     |
| `ni.observation.abstract`         | Shared behavior for observation-like models |
| `ni.observation.type`             | Observation type metadata                   |
| `ni.observation.category`         | Observation category metadata               |
| `ni.observation.interpretation`   | Observation interpretation vocabulary       |
| `ni.observation.reference.range`  | Reference ranges for interpretation         |
| `ni.observation.value.code`       | Coded value support                         |
| `ni.observation.sheet`            | Observation sheet helper model              |
| `ni.observation.vitalsign.mixin`  | Vital-sign-specific behavior                |
| `ni.observation.bloodgroup.mixin` | Blood-group-specific behavior               |

## Data, Reports, and UI

- `data/ni_observation_*` files seed categories, observation types, interpretations, and reference ranges.
- `data/uom_uom_data.xml` seeds units used by observation values.
- `wizard/ni_observation_wizard_views.xml` provides guided observation entry.
- `report/ni_patient_observation_view.xml`, `report/ni_encounter_observation_view.xml`, and `report/summary_report.xml` provide
  patient and encounter reporting.
- `ni.patient.observation` and `ni.encounter.observation` (`report/`) are SQL views of the latest valued observation per
  `(patient_id, type_id)` and per `(encounter_id, type_id)`: highest `occurrence`, ties broken by highest `id`. Rows without
  `type_id` or `occurrence` are left out, and the encounter view leaves out observations without an encounter.
- `static/src/component/list_renderer/*` and `static/src/scss/observation.scss` customize the backend list presentation.

## Security and Dependencies

- `security/ni_observation_group.xml` defines observation access.
- `security/ni_observation_security.xml` and `security/ir.model.access.csv` control record visibility and permissions.
- The module depends on `ni_patient`, `mail`, `uom`, and `uom_alias`.

## Pitfalls

- The latest-observation views use `NOT EXISTS` instead of `DISTINCT ON`, so PostgreSQL can apply the ORM's filter on `id` or
  `survey_response_id` before it picks the latest row. Do not switch back to `DISTINCT ON`: every read then rebuilds the view
  from the whole table.
- The anti-joins need the indexes `ni_observation__patient__ob_type__idx` and `ni_observation__encounter__ob_type__idx` on
  `(<key>, type_id, occurrence DESC, id)`, declared in `ni.observation.init()`. `tools.create_index()` skips a name that already
  exists, so a database with an older definition under the same name needs a manual rebuild.

## Verification

- Review `ni_observation/tests/test_compute_code.py` and `ni_observation/tests/test_inverse_value.py` after changing computed
  fields, inverse methods, or unit logic.
- Run `ni_observation/tests/test_latest_observation.py` after changing the latest-observation views.
- Re-check observation entry, sheet views, and patient or encounter reports after changes to reference data or UI components.
