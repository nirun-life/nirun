# Kanit Font (`l10n_th_web_font_kanit`)

## Purpose

Provides the Kanit typeface as a web asset for Odoo and applies it as the default UI font stack.

## Assets

- Registers Kanit `@font-face` definitions for the bundled Google font files across standard weights and italic variants.
- Loads `static/src/scss/fonts.scss` into `web.assets_common`.
- Applies the Kanit-based font family to the root document, body text, and heading styles.

## Dependencies

- `web`

## Notes

- The repository also contains `static/src/scss/backend.scss`, but only `fonts.scss` is declared in the manifest assets.
