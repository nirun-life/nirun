# Nirun - Body Site

Odoo 16.0 module that provides anatomical body-site coding for Nirun. It stores hierarchical body-structure terms so downstream
clinical modules can reference consistent body-site data instead of free-text anatomical labels.

## Purpose

`ni_body_site` is a small terminology module. It exists to centralize body-site coding and parent-child anatomical structure
data for modules such as medication or service workflows that need structured site selection.

## Main Models

| Model          | Role                                     |
| -------------- | ---------------------------------------- |
| `ni.body.site` | Hierarchical body-site dictionary record |

## Data and Views

- `data/ni.body.site.csv` and `data/ni_body_site_data.xml` seed the body-site vocabulary.
- `views/ni_body_site_views.xml` provides dictionary management for anatomical sites.

## Security and Dependencies

- `security/ir.model.access.csv` grants model permissions.
- The module depends on `ni_coding`.

## Verification

- Re-check parent-child hierarchy behavior and recursion protection after changing `ni.body.site` structure or import data.
- Confirm downstream modules that depend on body-site selection still show the expected anatomical vocabulary after terminology
  updates.
