# Patients - Summary Report (`ni_patient_summary_report`)

Odoo 16.0 module that provides summary, medical certificate, and signature-list reports built from the core patient record and
its related clinical modules.

## Purpose

`ni_patient_summary_report` collects the main clinical modules into printable patient-facing and provider-facing documents. It
also adds encounter-class actions and company options that control how some medical certificate content is rendered.

## Main Models

| Model                | Role                                                       |
| -------------------- | ---------------------------------------------------------- |
| `ni.encounter.class` | Adds report-print actions and a configurable summary title |
| `res.company`        | Adds medical certificate diagnosis and appendix settings   |

## Reports and Data

- `reports/summary_report*.xml` defines the patient summary report.
- `reports/medical_certificate_*.xml` defines the medical certificate report and template set.
- `reports/patient_signature_list_report*.xml` defines the signature list report.
- `data/ni_encounter_class_data.xml` seeds encounter classes used by the reporting workflow.
- `static/src/css/report.css` adds PDF-specific report styling through `web.report_assets_pdf`.

## Views and Behavior

- `model/ni_encounter_class.py` adds direct print actions for summary and medical certificate reports.
- `model/res_company.py` adds medical-certificate display settings such as diagnosis mode and appended recommendation HTML.
- `views/ni_encounter_class_views.xml` and `views/res_company_views.xml` expose those controls in the backend.

## Dependencies

- `ni_patient`
- `ni_allergy`
- `ni_observation`
- `ni_condition`
- `ni_procedure`
- `ni_medication`
- `ni_appointment`
- `ni_practitioner`
- `ni_communication`
- `ni_coverage`

## Verification

- Re-check all three printable outputs after report-template or CSS changes.
- Confirm encounter-class print actions still launch the correct reports.
- Review company-specific medical certificate settings whenever certificate output changes.
