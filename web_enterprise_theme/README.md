# Enterprise Theme (`web_enterprise_theme`)

## Purpose

Applies a customized enterprise-style backend theme for Odoo.

## Assets

- `web._assets_primary_variables` injects `_assets_primary_variables.scss` after Odoo's primary variable file.
- `web.assets_backend` loads `assets_backend.scss` with broader backend restyling.

## Theme Scope

- Overrides primary brand variables, text colors, link colors, required-field border colors, and border radius.
- Restyles forms, inputs, lists, notebooks, search view, buttons, chatter controls, and x2many list spacing.

## Dependencies

- `web`

## Notes

- The manifest marks this addon as `application=True`, so it is intended to be selectable as a full backend theme module rather
  than a tiny patch.
