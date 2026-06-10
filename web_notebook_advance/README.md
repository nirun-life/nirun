# Notebook Advance (`web_notebook_advance`)

## Purpose

Extends the backend notebook compiler and notebook component so XML notebook pages can carry extra presentation metadata.

## Main Components

- `FormCompiler` patch enhances notebook compilation to support page `icon`, `badge`, `info`, `orientation`, custom CSS classes,
  autofocus, and richer anchor tracking.
- `web.Notebook` template patch renders page icons and badges in notebook headers.

## Assets

- Loads `form_compiler.esm.js` and `core/notebook/notebook.xml` in `web.assets_backend`.

## Dependencies

- `web`

## Notes

- Supported notebook orientations include the original horizontal behavior plus the extra orientations consumed by companion
  modules such as `web_notebook_collapse`.
