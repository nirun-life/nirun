# Medication (`ni_medication`)

Odoo 16.0 module that manages medication definitions, dosage structures, medication requests, statements, dispensing, and
suggestion helpers for Nirun. It ties medication workflows to patient, condition, practitioner, and timing data so prescribing
stays structured and reusable.

## Purpose

`ni_medication` is the main prescribing and medication-tracking module in the repository. It combines master medication records
with reusable dosage logic and patient-linked medication workflows, including request, dispense, statement, and suggestion
flows.

## Main Models

| Model                                                                                                | Role                                                                                 |
| ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `ni.medication`                                                                                      | Master medication record, `_inherits` `product.template`                             |
| `ni.medication.abstract`                                                                             | Shared medication line behavior built on dosage data                                 |
| `ni.medication.dosage`                                                                               | Core dosage structure, `_inherit` `ni.timing.mixin`                                  |
| `ni.medication.request`                                                                              | Requested/prescribed medication workflow                                             |
| `ni.medication.statement`                                                                            | Recorded medication usage workflow                                                   |
| `ni.medication.dispense`                                                                             | Dispensing workflow                                                                  |
| `ni.medication.suggest` and `ni.medication.suggest.line`                                             | Suggestion catalog and line items                                                    |
| `ni.medication.ingredient`                                                                           | Ingredient composition lines                                                         |
| `ni.medication.form`, `ni.medication.unit`, `ni.medication.admin.location`, `ni.medication.dosage.*` | Supporting vocabularies for route, method, period, meal timing, and related metadata |

## Data, Views, and Reports

- `data/product_category_data.xml`, `data/uom_uom_data.xml`, and the `data/ni_medication_*` files seed medication vocabularies
  and dosage metadata.
- `views/ni_medication_views.xml`, `views/ni_medication_reqeust_views.xml`, `views/ni_medication_statement_views.xml`, and
  `views/ni_medication_dispense_views.xml` provide the core workflows.
- `views/ni_medication_dosage*.xml`, `views/ni_medication_form_views.xml`, and related dictionary views expose the supporting
  dosage structures.
- `wizard/ni_medication_suggest_wizard.py` and `wizard/ni_medication_suggest_wizard_views.xml` support guided suggestion flows.
- `reports/medication_label_report.xml` and `reports/medication_label_template.xml` provide medication label output.

## Security and Dependencies

- `security/ni_medication_group.xml` defines medication access groups.
- `security/ni_medication_rules.xml` and `security/ir.model.access.csv` control visibility and permissions.
- The module depends on `ni_body_site`, `ni_timing`, `ni_patient`, `ni_condition`, `ni_practitioner`, `product`, and
  `uom_alias`.

## Verification

- Re-check medication request, statement, dispense, and dosage flows after changing timing inheritance, vocabulary models, or
  wizard behavior.
