# Communication (`ni_communication`)

Odoo 16.0 module that records patient communications and contact events for Nirun. It tracks communication category, content,
sender, recipients, and sent or received timing so outreach and clinical contact activity can be stored as structured events.

## Purpose

`ni_communication` stores communication records that belong in the clinical history rather than general chatter. It is designed
for patient- and encounter-linked communication events with workflow state, identifier support, and recipient or sender
normalization.

## Main Models

| Model                       | Role                                                |
| --------------------------- | --------------------------------------------------- |
| `ni.communication`          | Core communication event record                     |
| `ni.communication.category` | Communication category vocabulary                   |
| `ni.communication.content`  | Communication content vocabulary linked to category |

## Workflow, Data, and Views

- `ni.communication` inherits workflow event behavior, identifier generation, and period fields so communication events
  integrate with the shared clinical timeline.
- `default_get()` can prefill recipients from the patient and sender information from the encounter performer.
- `data/ir_sequence_data.xml` and `data/ni_communication_category_data.xml` seed identifiers and category vocabulary.
- `views/ni_communication_views.xml`, `views/ni_communication_category_views.xml`, and
  `views/ni_communication_content_views.xml` provide the main communication UI.
- `views/ni_encounter_views.xml` and `views/ni_encounter_class_views.xml` expose communication behavior from encounter contexts.
- `wizard/ni_encounter_discharge_wizard.py` and `wizard/ni_encounter_discharge_wizard_views.xml` extend encounter discharge
  behavior for communication-related flows.

## Security and Dependencies

- `security/ir.model.access.csv` grants model permissions.
- `security/ni_procedure_group.xml` and `security/ni_procedure_security.xml` currently provide the module's additional security
  records.
- The module depends on `ni_patient` and `mail`.

## Verification

- Re-check sender and recipient defaulting, sender-partner normalization, and workflow summary behavior after changing
  communication creation logic.
- Re-check encounter-linked communication views and discharge-adjacent flows after changing communication category or content
  handling.
