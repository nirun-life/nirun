#  Copyright (c) 2023 NSTDA

{
    "name": "Noto Sans/Serif Thai Font",
    "summary": "Noto Sans/Serif Thai Font for Odoo",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Website",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["web"],
    "assets": {
        "web.assets_common": [
            "/l10n_th_web_font_noto/static/src/scss/fonts.scss",
        ],
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
