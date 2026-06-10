# Website - Hide Sign-in Button (`website_hide_signin`)

## Purpose

Hides the frontend website sign-in entry from the portal navigation.

## Views

- Inherits `portal.user_sign_in`.
- Replaces the `<li>` class expression so the sign-in menu item always includes `invisible`.

## Dependencies

- `website`

## Notes

- This module only affects the website template layer. It does not alter authentication behavior or portal access rules.
