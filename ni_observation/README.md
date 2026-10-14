# Observation (`ni_observation`)

Odoo 19.0 module that implements FHIR-style clinical observations for Nirun. It covers
measurements, laboratory values, vital signs, interpretation logic, and the supporting
reference data needed to store and display observations consistently.

## Purpose

`ni_observation` is the observation layer for the patient timeline. It builds on
`ni_patient` so clinicians can record structured measurements with units,
interpretation, categories, and reusable observation types instead of ad hoc text
fields.

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

- `data/ni_observation_*` files seed categories, observation types, interpretations, and
  reference ranges.
- `data/uom_uom_data.xml` seeds units used by observation values.
- `wizard/ni_observation_wizard_views.xml` provides guided observation entry.
- `report/ni_patient_observation_view.xml`, `report/ni_encounter_observation_view.xml`,
  and `report/summary_report.xml` provide patient and encounter reporting.
- `static/src/component/list_renderer/*` and `static/src/scss/observation.scss`
  customize the backend list presentation.

## Units of Measure

`data/uom_uom_data.xml` (`noupdate`) creates Nirun's units on the 19.0 UoM model: no
categories; a unit is `relative_factor` times its reference unit (`relative_uom_id`),
for example mg/dl = 0.01 kg/m³. The xmlids are the same as on 16.0-18.0 and every
conversion gives the same result.

Upgrading from 18.0 with OpenUpgrade: OpenUpgrade converts only units without an xmlid,
so `migrations/19.0.1.0.0/post-migration.py` converts Nirun's units from OpenUpgrade's
legacy columns (`relative_factor = 1 / factor`) and drops the old category xmlids. Pass
the repository's `upgrade_path/` as a second `--upgrade-path`; it also fixes
user-created "bigger" units, which OpenUpgrade 19 converts with an inverted ratio.

Known issue (from 16.0): `/sec` and `/hour` are defined as if they were time units (1
/min = 60 /sec), the inverse of a rate. Conversions are kept as they were; fix the data
before relying on frequency conversions.

## Display Names

- `ni.observation.sheet` displays its identifier; with the context key `show_occurrence`
  it adds the occurrence (used by the edit step of the wizard).
- `ni.observation.reference.range` displays `Type [low-high]`.
- `ni_observation` extends the patient display name through `ni.patient._name_get()`:
  with `show_gender_age`, it adds the blood group.

## Field Labels

From 18.0 every field has its own label (Odoo warns on duplicates): the typed value
fields are "Value (Text)", "Value (Integer)", "Value (Decimal)" and "Value (Code)", and
the aliases are "Effective Date" (`effective_date`) and "Observation Code" (`code_id`).
Views that show one value column keep the label "Value".

## List Widget

`ob_section_and_note_one2many` (with `ob_section_and_note_text`) shows observation lines
grouped by category sections. It is ported from the core `account` section-and-note
widget of the same Odoo version, so re-port it from that file on each upgrade instead of
patching it.

## Security and Dependencies

- `security/ni_observation_group.xml` defines observation access: from 19.0 the
  Viewer/User/Manager groups belong to the privilege "Observation".
- `security/ni_observation_security.xml` and `security/ir.model.access.csv` control
  record visibility and permissions.
- Reference data (categories, types, interpretations, reference ranges, value codes) is
  readable by every internal, portal and public user: from 18.0 each read rule is split
  into one row per `base.group_user`, `base.group_portal` and `base.group_public`.
- The module depends on `ni_patient`, `mail`, `uom`, and `uom_alias`.
- Soft dependency: the encounter form sets a `badge` attribute on the Vital Signs and
  Laboratory pages. Only `web_notebook_advance` shows it as a counter; without that
  module the views still load and the badge is not shown.

## Verification

- Review `ni_observation/tests/test_compute_code.py` and
  `ni_observation/tests/test_inverse_value.py` after changing computed fields, inverse
  methods, or unit logic.
- Re-check observation entry, sheet views, and patient or encounter reports after
  changes to reference data or UI components.
