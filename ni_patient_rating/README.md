# Patients - Rating (`ni_patient_rating`)

Odoo 16.0 module that adds post-encounter satisfaction links, QR codes, and rating views to patient encounters.

## Purpose

`ni_patient_rating` extends finished encounters with a lightweight feedback workflow so teams can request satisfaction ratings
and review the collected scores directly from the clinical record.

## Main Models

| Model          | Role                                                      |
| -------------- | --------------------------------------------------------- |
| `ni.encounter` | Extended with `rating.mixin`, rating link, and QR support |

## Workflow and UI

- `model/ni_encounter.py` adds `rating_last_value`, a computed rating URL, and a QR-code URL derived from the encounter’s rating
  access token.
- `action_send_rating_mail()` sends the rating request using the module’s email template once an encounter is finished.
- `views/ni_encounter_views.xml` adds a header action for feedback requests, a stat button for collected ratings, and a feedback
  notebook page showing either the latest rating or the shareable link and QR code.
- `static/src/scss/rating.scss` styles the rating-related backend presentation.

## Dependencies

- `ni_patient`
- `ni_practitioner`
- `rating`

## Verification

- Re-check finished-encounter feedback flows, especially mail sending, rating-link generation, and stat button visibility.
- Confirm the feedback tab switches correctly between “request pending” and “rating received” states.
