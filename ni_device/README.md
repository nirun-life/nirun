# Device (`ni_device`)

Odoo 16.0 module that manages medical devices, device definitions, holder workflows, repair tracking, and usage logging for
Nirun. It also connects device activity back into observation and patient contexts so equipment use can be tracked alongside
clinical records.

## Purpose

`ni_device` covers the operational lifecycle of medical devices after they enter the system. It supports master device
definitions, issued device instances, holder changes, repair and disposal requests, and usage records that can be surfaced from
patient and observation views.

## Main Models

| Model                    | Role                                                   |
| ------------------------ | ------------------------------------------------------ |
| `ni.device`              | Core device instance record                            |
| `ni.device.definition`   | Master device definition and model metadata            |
| `ni.device.type`         | Device type vocabulary                                 |
| `ni.device.dispose.type` | Disposal-type vocabulary                               |
| `ni.device.request`      | Device holder, transfer, return, and disposal workflow |
| `ni.device.repair`       | Repair and damage workflow                             |
| `ni.device.usage`        | Device usage record                                    |
| `ni.device.holder`       | Holder history record                                  |
| `ni.holder.mixin`        | Shared holder-related fields and name logic            |
| `ni.device.label.layout` | Device label printing helper                           |

## Workflow, Data, and Views

- `ni.device` inherits patient linkage, identifier support, and device-specific workflow actions for hold, return, transfer, and
  disposal requests.
- `ni.device.definition` carries a default `price`, applied to a new `ni.device` only when the device's own price is still unset
  (one-time default, not resynced on later definition changes — see `docs/adr/0001-price-one-time-default.md`).
- Once a device has any `ni.device.request` (regardless of state), its `definition_id` is locked: `ni.device.write()` raises a
  `UserError` and the form field becomes readonly (see `docs/adr/0002-definition-lock-any-request.md`).
- `data/ir_sequence_data.xml` and `data/ni_device_definition_data.xml` seed identifiers and base device definitions.
- `views/ni_device_views.xml`, `views/ni_device_request_views.xml`, `views/ni_device_repair_views.xml`,
  `views/ni_device_usage_views.xml`, and related definition or holder views provide the main operational UI.
- `views/ni_observation_views.xml`, `views/ni_observation_sheet_views.xml`, and `views/ni_patient_views.xml` expose device
  activity from clinical contexts. The device form's "Create Observation Sheet" button opens
  `wizard/ni_device_create_observation_sheet.py`, which prompts for a patient and creates a sheet pre-populated with one line
  per the device's `observation_type_ids`.
- `ni.device.usage` has optional `latitude`/`longitude` fields for recording where a usage event happened.
- `wizard/ni_device_report_lost.py` and `wizard/ni_device_report_lost_wizard.xml` support the lost-device reporting flow.
- `report/device_label_layout_template.xml` provides device label output.

## Security and Dependencies

- `security/ir.model.access.csv` grants model permissions.
- `security/ir_rule_data.xml` constrains device visibility.
- The module depends on `ni_observation`.

## Verification

- Review `ni_device/tests/test_ni_device.py` after changing device defaults, definition propagation, repair workflow, or request
  approval behavior.
- Re-check patient, observation, holder, repair, and label-printing flows after changing device lifecycle logic.
