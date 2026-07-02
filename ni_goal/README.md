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
  `target_code_ids` (a set of acceptable `ni.observation.value.code` values) with `target_code_operator` describing how they
  should be matched. `ni.goal.code` carries the same target shape as a reusable template, copied onto `ni.goal` on selection.

## Security and Dependencies

- `security/ir.model.access.csv` grants model permissions.
- The module depends on `ni_patient`, `ni_observation`, and `ni_condition`.

## Verification

- Re-check goal state transitions, wizard behavior, and mail-thread comments after changes to `ni.goal` state or achievement
  logic.
- Confirm observation-linked fields such as baseline, latest, and outcome values still update correctly after changing goal or
  observation integration.
