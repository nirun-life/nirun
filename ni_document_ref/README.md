# Document Reference (`ni_document_ref`)

Odoo 16.0 module that manages clinical document references and attached files for Nirun. It links authored documents into the
patient workflow timeline, with document type defaults, co-author handling, printable output, and summary reporting.

## Purpose

`ni_document_ref` stores structured clinical documents rather than untyped attachments. It is designed for documents that belong
in the clinical record, with workflow state, authorship, type and category metadata, and printable output.

## Main Models

| Model                      | Role                           |
| -------------------------- | ------------------------------ |
| `ni.document.ref`          | Core document reference record |
| `ni.document.ref.type`     | Document type vocabulary       |
| `ni.document.ref.category` | Document category vocabulary   |

## Workflow, Data, and Views

- `ni.document.ref` inherits workflow event behavior and identifier generation so document records appear in the shared clinical
  timeline.
- `default_get` applies a practitioner-specific default document type from the current user's job, and `create()` can add the
  current user as a co-author automatically.
- `data/ni_document_ref_category_data.xml`, `data/ni_document_ref_type_data.xml`, and `data/ir_sequence_data.xml` seed document
  metadata and identifiers.
- `views/ni_document_ref_views.xml`, `views/ni_document_ref_type_views.xml`, and `views/ni_document_ref_category_views.xml`
  provide the main document UI.
- `reports/ni_document_ref_report.xml`, `reports/ni_document_ref_templates.xml`, and `reports/summary_report.xml` provide
  document printing and summary output.
- `static/src/scss/kanban.scss` customizes backend kanban presentation.

## Security and Dependencies

- `security/ir.model.access.csv` grants model permissions.
- `security/ni_document_ref_rule.xml` constrains document visibility.
- The module depends on `ni_patient`.

## Verification

- Re-check practitioner-specific default type selection, co-author population, and attachment-count behavior after changing
  `ni.document.ref` creation logic.
- Re-check document printing, kanban presentation, and encounter-linked document views after changing type, category, or report
  behavior.
