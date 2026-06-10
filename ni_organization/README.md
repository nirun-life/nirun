# Organization (`ni_organization`)

Odoo 16.0 module that extends `res.company` into a healthcare organization record with typed facilities, shared identifiers, and
searchable capacity metadata.

## Purpose

`ni_organization` provides the organization and facility layer used by Nirun deployments. It lets each Odoo company carry a
clinical identifier, a typed organization hierarchy, and simple capacity information that can be reused by downstream modules.

## Main Models

| Model              | Role                                                         |
| ------------------ | ------------------------------------------------------------ |
| `res.company`      | Organization record with identifier, type, and capacity      |
| `res.company.type` | Organization type vocabulary built on `ni.coding`            |
| `res.partner`      | Stores the shared unique identifier used by company partners |

## Behavior and Data

- `models/res_company.py` renames the main company label to `Organization Name`, exposes the related identifier, and adds
  `type_id`, `capacity`, `capacity_unit`, and computed `display_capacity`.
- Organization names use a custom `name_get` and `_name_search` so users can search by either organization name or identifier.
- `models/res_company_type.py` defines a parent-child coding hierarchy for organization types and blocks recursive structures.
- `data/res_company_type_data.xml` seeds the base organization type records used by the type selector.

## Views and Security

- `views/res_company_views.xml` adds the healthcare organization fields onto the company form.
- `views/res_company_type_views.xml` provides maintenance views for the organization type hierarchy.
- `security/ir.model.access.csv` grants access to the custom organization type model.

## Dependencies

- `base`
- `ni_identifier`
- `ni_coding`

## Verification

- Re-check organization create and edit flows, especially identifier search and the displayed organization label.
- Confirm organization type hierarchy edits reject recursive parent assignments.
