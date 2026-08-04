# Noto Sans/Serif Thai Font (`l10n_th_web_font_noto`)

## Purpose

Provides a compact Noto Sans web-font set with Thai glyph coverage and separate Noto Sans/Noto Serif report fonts, then exposes
the report families to Odoo's company font selection and applies Noto Sans to the UI.

## Main Components

- `res.company` extension adds `NotoSans` and `NotoSerif` to the company `font` selection.
- Web assets load WOFF2 font-face declarations and default UI typography styles through `web.assets_common`.
- Report assets load regular Thai TTF declarations through `web.report_assets_common` for wkhtmltopdf compatibility.

## Assets

- `fonts.scss` defines basic-Latin and Thai `@font-face` rules for the Noto Sans web family. Every face uses
  `font-display: swap` so fallback text remains visible while fonts load.
- `common.scss` sets the default frontend/backend font stack to `NotoSans`.
- `report.scss` declares report-time Thai regular TTF fonts for `NotoSans` and `NotoSerif`.

### Web font contract

- Upright weights: 300, 400, 500, 600, and 700.
- Italic weights: 400, 500, and 700 for basic Latin. Thai text uses the closest upright Thai face and browser synthesis when an
  italic style is requested because the upstream Noto Sans Thai family has no italic files.
- Thai subset: the Thai Unicode block, zero-width shaping controls, and dotted circle.
- Basic-Latin subset: ASCII, general punctuation, currency symbols, arrows, minus sign, dotted circle, byte-order mark, and the
  replacement character. Characters outside this contract use the system fallback font.

The compiled Odoo stylesheet is fingerprinted and receives Odoo's one-year immutable cache policy. Direct WOFF2 static resources
use Odoo's standard one-week public static-file cache policy. Production proxies must preserve these headers.

### Regenerating WOFF2 assets

The generated WOFF2 files are runtime artifacts. The larger source TTF files are intentionally not shipped except for the two
report faces. Install the pinned FontTools and Brotli versions outside the addon, then provide an external directory containing
the `NotoSans` and `NotoSansThai` source folders:

```text
python -m pip install -r l10n_th_web_font_noto/tools/requirements.txt
python l10n_th_web_font_noto/tools/generate_web_fonts.py --source-dir /path/to/google
```

The generator owns the face inventory and glyph ranges and verifies the SHA-256 digest of every source TTF. Keep its range
constants synchronized with `fonts.scss` whenever the asset contract changes.

## Dependencies

- `web`

## Notes

- The module changes the available company report-font choices but does not add a separate configuration view in this addon; it
  extends an existing `res.company` selection field.
- Report fonts intentionally remain TTF and separate from browser WOFF2 assets because wkhtmltopdf compatibility is required.
