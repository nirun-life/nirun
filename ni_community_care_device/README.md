# Community Care Device (`ni_community_care_device`)

Odoo 16.0 module that surfaces device-usage history from `ni_device` inside the community-care patient form.

## Purpose

`ni_community_care_device` is a small integration addon that connects community-care patient screens with device usage records,
making it easier to inspect assigned or used medical devices during community follow-up.

## Main Behavior

- `views/ni_patient_views.xml` adds a smart button to the simplified community-care patient form.
- The button launches `ni_device.ni_device_usage_action_by_patient` and displays `device_usage_count` as the stat value.
- The integration relies on the patient view provided by `ni_community_care` and the usage action supplied by `ni_device`.

## Dependencies

- `ni_community_care`
- `ni_device`

## Verification

- Re-check the community-care patient form to confirm the smart button appears when device usage exists.
- Confirm the action opens the expected device-usage records for the selected patient.
