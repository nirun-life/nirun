# Notebook Collapse (`web_notebook_collapse`)

## Purpose

Builds on `web_notebook_advance` to render notebook pages as collapsible accordion sections, with optional multi-column layout
and collapse/expand controls.

## Main Components

- `Notebook` patch adds `collapXpand()` plus lifecycle hooks that support accordion behavior and masonry relayout.
- Notebook template patch replaces the base notebook rendering with horizontal, vertical, and original modes backed by accordion
  markup.
- SCSS styles collapse controls, accordion headers, pane layout, x2many spacing, and the vertical card-like presentation.

## Assets

- Loads bundled Masonry JS, notebook XML, notebook JS, and notebook SCSS in `web.assets_backend`.

## Dependencies

- `web`
- `web_notebook_advance`

## Notes

- The vertical orientation loads Masonry from a CDN in the template and uses it to lay out notebook cards.
- Collapse/expand controls are shown only when the notebook has more than three visible pages and the orientation is not
  `original`.
