# Asterisk Label (`web_form_label_asterisk`)

## Purpose

Adds a visible asterisk to required field labels in backend forms.

## Assets

- JavaScript patch extends `FormLabel.className` so required fields receive `o_form_label_required` alongside Odoo's other
  visual-feedback classes.
- XML template patch injects `<span class="o_form_label_asterisk">*</span>` before the existing `<sup>` in `web.FormLabel`.
- SCSS hides the asterisk by default and shows it only when the label has `o_form_label_required`.

## Dependencies

- `web`

## Notes

- This module changes the label component globally for backend forms once installed.
