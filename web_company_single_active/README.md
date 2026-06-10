# No Multi-Company Active (`web_company_single_active`)

## Purpose

Prevents users from actively toggling more than one company at a time in the backend company switcher UI.

## Assets

- Loads `static/src/scss/main.scss` into `web.assets_backend`.
- Hides `.toggle_company` inside the switch-company menu and adjusts the adjacent login entry height.

## Dependencies

- `web`

## Notes

- This module is CSS-only. It changes the backend company-switcher presentation without adding Python models or views.
