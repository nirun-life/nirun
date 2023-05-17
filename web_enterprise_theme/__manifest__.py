#  Copyright (c) 2023 NSTDA

{
    "name": "Enterprise Theme",
    "summary": "Odoo Enterprise Theme",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Themes/Backend",
    "author": "NSTDA, Piruin P.",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["web"],
    "assets": {
        "web._assets_primary_variables": [
            (
                "after",
                "web/static/src/scss/primary_variables.scss",
                "/web_enterprise_theme/static/src/scss/_assets_primary_variables.scss",
            ),
        ],
        "web.assets_backend": [
            "/web_enterprise_theme/static/src/scss/assets_backend.scss",
        ],
    },
    "application": True,
    "auto_install": False,
    "installable": True,
}
