# Disability — Thai Localization (`l10n_th_ni_patient_disability`)

Odoo 16.0 module extending the Nirun healthcare platform with **Thai disability tracking** aligned to HL7 FHIR Observation.
Records disability status and the 7-category Thai disability classification per patient, surfaces disabled patients in dedicated
views, and can auto-elevate encounter triage priority for patients with a disability.

## After Install

### Patient list

A **Disability** column appears (optional, shown by default). Patients with a confirmed disability observation show `✓`.

### Patient form

Two read-only fields appear below the current encounter field:

- **Has Disability** — boolean badge, visible only when `True`
- **Disability Types** — tag list of the patient's Thai disability categories (TH-DIS-01 … TH-DIS-07)

Both update automatically whenever a disability observation is recorded or changed.

### Patient search / filters

New filters in the patient search bar:

| Filter         | Domain                    |
| -------------- | ------------------------- |
| Has Disability | `has_disability = True`   |
| Visual         | TH-DIS-01 (การมองเห็น)    |
| Hearing        | TH-DIS-02 (การได้ยิน)     |
| Mobility       | TH-DIS-03 (การเคลื่อนไหว) |
| Mental         | TH-DIS-04 (จิตใจ)         |
| Intellectual   | TH-DIS-05 (สติปัญญา)      |
| Learning       | TH-DIS-06 (การเรียนรู้)   |
| Autistic       | TH-DIS-07 (ออทิสติก)      |

### Patient menu — Patients with Disability

A new menu entry **Patients with Disability** appears under the Patient root menu. Opens a pre-filtered patient list showing
only patients where `has_disability = True`.

### Encounter search

A **Patient has Disability** filter is added to the encounter search, allowing staff to find all encounters for patients with a
disability.

## How to Record Disability

Disability is stored as `ni.observation` records (FHIR Observation):

1. Open a patient or encounter.
2. In the **Observations** section, add a new observation sheet or inline observation.
3. Select observation type **Disability Status** — choose **มีความพิการ (Disabled)** or **ไม่มีความพิการ (Not Disabled)**.
4. Optionally add a second observation with type **Thai Disability Type** and select one or more of the 7 categories.

`has_disability` and `disability_type_ids` on the patient update automatically.

## Configuration

### Encounter priority for patients with disability

Go to **Settings → Companies → (select company) → Encounter tab**.

Set **Disability Encounter Priority** to the desired triage level:

| Value   | Thai       |
| ------- | ---------- |
| Routine | ปกติ       |
| Urgent  | เร่งด่วน   |
| ASAP    | รีบด่วน    |
| STAT    | ด่วนที่สุด |

When set, any **new encounter** created for a patient whose `has_disability = True` will have its priority pre-filled to this
value. Leave blank to disable the feature (encounters default to Routine as normal).

> Priority is applied at creation time only. Changing the company setting does not retroactively update existing encounters.

## Dependencies

- `ni_patient` — patient, encounter, and company models
- `ni_observation` — observation recording and category system
- `ni_coding` — base coding model
