# Patients - Rating (`ni_patient_rating`)

Odoo 16.0 module that adds post-encounter satisfaction links, QR codes, and rating views to patient encounters.

## Purpose

`ni_patient_rating` extends finished encounters with a lightweight feedback workflow so teams can request satisfaction ratings
and review the collected scores directly from the clinical record.

## Main Models

| Model          | Role                                                                           |
| -------------- | ------------------------------------------------------------------------------ |
| `ni.encounter` | Extended with `rating.mixin`, rating link, and QR support                      |
| `ni.patient`   | Extended with `rating.parent.mixin` to aggregate ratings across its encounters |

## Workflow and UI

- `model/ni_encounter.py` adds `rating_last_value`, a computed rating URL, and a QR-code URL derived from the encounter’s rating
  access token. It also overrides `_rating_get_parent_field_name()` to link each encounter rating to its patient via
  `patient_id`, which feeds the patient-level aggregate below.
- `action_send_rating_mail()` sends the rating request using the module’s email template once an encounter is finished.
- `model/ni_patient.py` applies `rating.parent.mixin` so `ni.patient` exposes `rating_ids`, `rating_count`, `rating_avg`, and
  `rating_percentage_satisfaction` computed from all of the patient's encounter ratings. Only ratings created after this linkage
  was added carry the parent link — pre-existing ratings are not backfilled.
- `views/ni_encounter_views.xml` adds a header action for feedback requests, a stat button for collected ratings, and a feedback
  notebook page showing either the latest rating or the shareable link and QR code.
- `views/ni_patient_views.xml` adds a stat button to the patient form showing the patient's average rating across encounters.
- `static/src/scss/rating.scss` styles the rating-related backend presentation.

## Dependencies

- `ni_patient`
- `ni_practitioner`
- `rating`

## Verification

- Re-check finished-encounter feedback flows, especially mail sending, rating-link generation, and stat button visibility.
- Confirm the feedback tab switches correctly between “request pending” and “rating received” states.
- `tests/test_ni_patient_rating.py` covers the patient-level rating aggregation (`_rating_get_parent_field_name` linkage and
  `rating.parent.mixin` totals). Note: `ni.patient.rating_ids` must be explicitly invalidated after creating/consuming a rating
  in the same transaction — its inverse (`parent_res_id`) is a plain Integer, not a Many2one, so the ORM cannot auto-invalidate
  the cached One2many.
