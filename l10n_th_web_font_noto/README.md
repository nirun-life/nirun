# Noto Sans/Serif Thai Font (`l10n_th_web_font_noto`)

## Purpose

Provides bundled Noto Sans and Noto Serif web/report fonts with Thai glyph coverage, then exposes those families to Odoo's
company font selection and default UI styling.

## Main Components

- `res.company` extension Adds `NotoSans` and `NotoSerif` to the company `font` selection.
- Web assets Loads shared font-face declarations and default UI typography styles through `web.assets_common`.
- Report assets Loads Thai-focused report `@font-face` declarations through `web.report_assets_common`.

## Assets

- `fonts.scss` Defines Latin and Thai `@font-face` rules for Noto Sans and Noto Serif families.
- `common.scss` Sets the default frontend/backend font stack to `NotoSans`.
- `report.scss` Declares report-time Thai regular fonts for `NotoSans` and `NotoSerif`.

## Dependencies

- `web`

## Notes

- The module changes the available company font choices but does not add a separate configuration view in this addon; it extends
  an existing `res.company` selection field.
