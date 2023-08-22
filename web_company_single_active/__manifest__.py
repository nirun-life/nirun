#  Copyright (c) 2023 NSTDA

{
    "name": "No Multi-Company Active",
    "summary": "This module prevent user from active more than one company at time",
    "version": "16.0.0.1.0",
    "development_status": "Alpha",
    "category": "Website",
    "author": "Pop Lacto, DADOS, NSTDA",
    "website": "https://nirun.life/",
    "license": "LGPL-3",
    "maintainers": ["piruin"],
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "/web_company_single_active/static/src/scss/main.scss",
        ],
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
