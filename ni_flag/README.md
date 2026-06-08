# Flag (`ni_flag`)

Odoo 16.0 module implementing the HL7 FHIR R4 Flag resource for the Nirun healthcare platform. It records prospective warnings
and safety notes about a patient and now supports observation-driven flag recommendations with evidence and conflict handling.

## After Install

### Patient form

A row of colored tag badges appears directly below the patient name, one badge per active patient-level flag.

### Encounter form

Patient flags and encounter flags appear near the title for quick scanning, and a smart button links staff to pending flag
recommendations for the encounter.

### Patient kanban and encounter lists

Active flags are visible directly on patient cards and encounter list or kanban views so triage staff can scan records without
opening each form.

### Flags report

The Flags menu includes list, pivot, and graph reporting with origin and evidence fields. A separate Flag Recommendations menu
defaults to pending recommendations.

## Observation-driven flag recommendations

Flag recommendation rules map observation types and optional interpretation or value-code matches to flag codes. Rules recommend
by default. Admins may mark selected rules as auto-apply.

Recommended and auto-created flags keep the source observation on the flag detail form so staff can see why the flag exists.

## Conflicting flags

Flag codes can define conflicting flag codes. When a user accepts a recommendation that conflicts with active flags, a
confirmation wizard shows the flags that will be deactivated. Auto-apply rules deactivate conflicting flags automatically and
close the old flags with `period_end`.

## Dependencies

- `ni_patient`
- `ni_period`
- `ni_identifier`
- `ni_observation`
