# Goal (`ni_goal`)

Odoo 16.0 module that tracks patient care goals, goal state, and achievement progress for Nirun. It connects goals to
observations and conditions so teams can monitor target outcomes against real patient measurements.

## Purpose

`ni_goal` is the goal-tracking layer for care management. It stores patient-specific goals, links them to condition context and
observation measures, and provides a guided state-change workflow that can record comments and achievement changes.

## Main Models

| Model                  | Role                            |
| ---------------------- | ------------------------------- |
| `ni.goal`              | Core patient goal record        |
| `ni.goal.code`         | Goal terminology dictionary     |
| `ni.goal.category`     | Goal category vocabulary        |
| `ni.goal.state`        | Goal state vocabulary           |
| `ni.goal.achievement`  | Goal achievement vocabulary     |
| `ni.goal.state.wizard` | Guided goal state-change wizard |

## Workflow, Data, and Views

- `ni.goal` inherits patient linkage, period fields, and mail tracking so goal progress stays visible over time.
- `wizards/ni_goal_state_wizard.py` and `wizards/ni_goal_state_wizard_views.xml` provide the guided state-transition flow,
  including optional comments and achievement selection.
- `datas/ni_goal_state_data.xml` and `datas/ni_goal_achievement_data.xml` seed the state and achievement vocabularies.
- `views/ni_goal_views.xml`, `views/ni_goal_state_views.xml`, `views/ni_goal_achievement_views.xml`, and related code or
  category views provide the goal management UI.
- `views/ni_encounter_views.xml` links goals into encounter workflows, and `views/ni_condition_code_views.xml` exposes the
  condition-to-goal coding relationship.
- A goal's measure is an `ni.observation.type` (`observation_type_id`), restricted to `int`/`float`/`code_id`/`code_ids` value
  types. Numeric measures use `target_min`/`target_max`; Single Choice (`code_id`) and Multi Choice (`code_ids`) measures use
  `target_code_ids` (a set of acceptable `ni.observation.value.code` values) with `target_code_operator` deciding how the
  observed value(s) on the latest matching observation must relate to that set (implemented in `ni.goal._match_target_code`):

  - `=` (Match) — the observed values are exactly the same set as the target set (order doesn't matter).
  - `!=` (Not Match) — the observed values are not exactly the same set as the target set.
  - `in` (Contain) — every observed value is a member of the target set (the observed set may be a subset).
  - `not in` (Not Contain) — no observed value is a member of the target set (fully disjoint).
  - `child_of` (Child of) — every observed value is a descendant of, or equal to, some target value, walking
    `ni.observation.value.code`'s `parent_id` hierarchy.
  - `parent_of` (Parent of) — every observed value is an ancestor of, or equal to, some target value, walking the same
    hierarchy.

  `ni.goal.code` carries the same target shape (including `target_code_operator`) as a reusable template, copied onto `ni.goal`
  on selection.

- For numeric measures, `ni.goal.code.target_type` decides how the template's `target_min`/`target_max` are derived when applied
  to a goal (in `ni.goal._onchange_code_id`):

  - `fix` (Fix Value) — `target_fix_min`/`target_fix_max` are copied onto the goal's `target_min`/`target_max` as-is, a fixed
    absolute range.
  - `ratio` (Ratio) — the goal's `target_min`/`target_max` are computed as the patient's current observation value multiplied by
    `target_ratio_min`/`target_ratio_max` (e.g. a ratio of `0.9`-`1.1` targets within 90%-110% of the patient's value at the
    time the goal is created), so the range is relative to that patient rather than a fixed number.

- `target_status` (computed, not stored) compares the latest observation (`observation_id`) against the target and renders as an
  "In Target"/"Out of Target" badge on the goal form and the state wizard. `target_alert_message` (computed) warns on the state
  wizard when there isn't enough evidence to judge progress: no baseline (`address_observation_id`) has been recorded yet, or a
  baseline exists but the latest observation is still that same baseline record (nothing measured since).

## Security and Dependencies

- `security/ir.model.access.csv` grants model permissions.
- The module depends on `ni_patient`, `ni_observation`, and `ni_condition`.

## Verification

- Re-check goal state transitions, wizard behavior, and mail-thread comments after changes to `ni.goal` state or achievement
  logic.
- Confirm observation-linked fields such as baseline, latest, and outcome values still update correctly after changing goal or
  observation integration.
