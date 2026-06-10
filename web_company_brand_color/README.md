# Web Company Brand Color (`web_company_brand_color`)

## Purpose

Adds editable company brand colors and a helper that derives those colors from the company logo.

## Main Components

- `res.company` extension Stores brand colors in serialized sparse field `brand_colors` with `primary_color`,
  `primary_dark_color`, `primary_light_color`, and `text_color`.
- `button_compute_color()` Reads the company logo, estimates a dominant color, derives darker/lighter variants, and chooses
  black or white text for contrast.
- Utility helpers `utils.py` provides image decoding and RGB normalization helpers using Pillow.

## Views

- Company form: adds a `Company Styles` page for system users with the color fields and a `Compute from logo` button.

## Dependencies

- `web`
- `base_sparse_field`

## Notes

- Color extraction ignores white pixels and downscales the logo before sampling.
- This module is described in the manifest as a modified version of OCA's `web_company_color`.
