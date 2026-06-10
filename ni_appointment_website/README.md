# Appointment Website (`ni_appointment_website`)

Odoo 16.0 module that adds a public-facing website search and booking flow on top of the Nirun appointment module.

## Purpose

`ni_appointment_website` lets website users find a provider organization, choose an appointment slot, and create an
`ni.appointment` from the frontend. It complements the backend and portal flows in `ni_appointment` with a clinic-search and
booking entry point.

## Main Components

| Component                           | Role                                                                             |
| ----------------------------------- | -------------------------------------------------------------------------------- |
| `controller/main.py`                | Website routes for provider search, booking form, submit, and availability check |
| `views/ni_appointment_template.xml` | Company search and booking templates                                             |
| `static/js/appointment.js`          | Frontend availability counter for practitioner/date/time                         |

## Workflow and Behavior

- `/appointment` shows a provider search page and redirects directly to the booking form when only one company exists.
- `/appointment/form` renders the booking form for an authenticated website user and loads departments and practitioners for the
  selected company.
- `/appointment/submit` creates or reuses a patient record, rounds requested time to 30-minute slots, creates an
  `ni.appointment`, activates it to populate attendees, and then resets the state back to draft before redirecting to the portal
  detail page.
- `appointment_check()` returns the number of overlapping draft or active appointments for the selected practitioner and slot.

## Data, Views, and Assets

- `data/website_data.xml` configures website-side data needed by the booking flow.
- `views/ni_appointment_template.xml` defines both the provider search page and the booking form.
- `static/js/appointment.js` calls `/appointment/check` whenever practitioner, date, and time are all selected.

## Dependencies

- `ni_appointment`
- `website`
- `partner_location`

## Verification

- Re-check the full website booking flow, including provider search, patient reuse or creation, and redirect to the appointment
  detail page.
- Confirm the availability counter updates correctly for practitioner and time changes.
- Review the caregiver-booking path carefully because the controller notes duplicate-patient risk when auto-registering someone
  other than the logged-in user.
